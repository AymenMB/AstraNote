-- Database initialization script for NotebookLM RAG System
-- This script creates the necessary tables and initial data

-- Create database (if using a separate database creation step)
-- CREATE DATABASE notebooklm_rag;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    notebook_id VARCHAR(255) UNIQUE,
    organization VARCHAR(255),
    department VARCHAR(255),
    bio TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    title VARCHAR(500),
    description TEXT,
    content_preview TEXT,
    metadata JSONB,
    notebooklm_document_id VARCHAR(255) UNIQUE,
    processing_status VARCHAR(50) DEFAULT 'pending' NOT NULL,
    processing_error TEXT,
    query_count INTEGER DEFAULT 0 NOT NULL,
    last_queried_at TIMESTAMP WITH TIME ZONE,
    owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Queries table
CREATE TABLE IF NOT EXISTS queries (
    id SERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
    query_type VARCHAR(50) DEFAULT 'semantic' NOT NULL,
    response_text TEXT,
    response_sources JSONB,
    response_metadata JSONB,
    execution_time REAL,
    tokens_used INTEGER,
    status VARCHAR(50) DEFAULT 'pending' NOT NULL,
    error_message TEXT,
    conversation_id VARCHAR(255),
    parent_query_id INTEGER REFERENCES queries(id),
    context JSONB,
    user_rating INTEGER CHECK (user_rating >= 1 AND user_rating <= 5),
    user_feedback TEXT,
    relevance_score REAL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Audit logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    event_description TEXT NOT NULL,
    resource_type VARCHAR(100),
    resource_id VARCHAR(255),
    ip_address INET,
    user_agent TEXT,
    request_method VARCHAR(10),
    request_path VARCHAR(500),
    request_params JSONB,
    response_status INTEGER,
    response_time INTEGER,
    metadata JSONB,
    correlation_id VARCHAR(255),
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_notebook_id ON users(notebook_id);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

CREATE INDEX IF NOT EXISTS idx_documents_owner_id ON documents(owner_id);
CREATE INDEX IF NOT EXISTS idx_documents_processing_status ON documents(processing_status);
CREATE INDEX IF NOT EXISTS idx_documents_notebooklm_id ON documents(notebooklm_document_id);
CREATE INDEX IF NOT EXISTS idx_documents_file_type ON documents(file_type);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at);

CREATE INDEX IF NOT EXISTS idx_queries_user_id ON queries(user_id);
CREATE INDEX IF NOT EXISTS idx_queries_conversation_id ON queries(conversation_id);
CREATE INDEX IF NOT EXISTS idx_queries_status ON queries(status);
CREATE INDEX IF NOT EXISTS idx_queries_created_at ON queries(created_at);
CREATE INDEX IF NOT EXISTS idx_queries_parent_query_id ON queries(parent_query_id);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_event_type ON audit_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_correlation_id ON audit_logs(correlation_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);

-- Create function to automatically update updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_queries_updated_at BEFORE UPDATE ON queries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_audit_logs_updated_at BEFORE UPDATE ON audit_logs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert initial admin user (password: "admin123" - change in production!)
-- Password hash for "admin123" using bcrypt
INSERT INTO users (
    username, 
    email, 
    full_name, 
    hashed_password, 
    is_admin, 
    is_verified, 
    is_active
) VALUES (
    'admin', 
    'admin@notebooklm-rag.com', 
    'System Administrator', 
    '$2b$12$rYKhHrZvJH.6mXNyQ5hZPu0wKFJU0.OjV1VQi.sJ9zV4vQsZwJY.O', 
    TRUE, 
    TRUE, 
    TRUE
) ON CONFLICT (username) DO NOTHING;

-- Insert sample data for development (optional)
-- This can be removed in production

-- Sample user
INSERT INTO users (
    username, 
    email, 
    full_name, 
    hashed_password, 
    is_admin, 
    is_verified, 
    is_active,
    organization,
    department
) VALUES (
    'testuser', 
    'testuser@example.com', 
    'Test User', 
    '$2b$12$rYKhHrZvJH.6mXNyQ5hZPu0wKFJU0.OjV1VQi.sJ9zV4vQsZwJY.O', 
    FALSE, 
    TRUE, 
    TRUE,
    'Example Corp',
    'Engineering'
) ON CONFLICT (username) DO NOTHING;

-- Create extension for UUID generation if not exists
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Grant permissions (adjust as needed for your environment)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO notebooklm_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO notebooklm_user;

-- Views for common queries
CREATE OR REPLACE VIEW user_stats AS
SELECT 
    u.id,
    u.username,
    u.full_name,
    COUNT(DISTINCT d.id) as document_count,
    COUNT(DISTINCT q.id) as query_count,
    AVG(q.user_rating) as avg_rating,
    MAX(q.created_at) as last_query_at,
    MAX(d.created_at) as last_upload_at
FROM users u
LEFT JOIN documents d ON u.id = d.owner_id AND d.is_active = TRUE
LEFT JOIN queries q ON u.id = q.user_id AND q.is_active = TRUE
WHERE u.is_active = TRUE
GROUP BY u.id, u.username, u.full_name;

-- View for document statistics
CREATE OR REPLACE VIEW document_stats AS
SELECT 
    d.file_type,
    COUNT(*) as count,
    AVG(d.file_size) as avg_size,
    SUM(d.file_size) as total_size,
    AVG(d.query_count) as avg_queries
FROM documents d
WHERE d.is_active = TRUE AND d.processing_status = 'completed'
GROUP BY d.file_type;

-- View for query performance
CREATE OR REPLACE VIEW query_performance AS
SELECT 
    DATE(q.created_at) as query_date,
    COUNT(*) as total_queries,
    COUNT(CASE WHEN q.status = 'completed' THEN 1 END) as successful_queries,
    COUNT(CASE WHEN q.status = 'failed' THEN 1 END) as failed_queries,
    AVG(q.execution_time) as avg_execution_time,
    AVG(q.user_rating) as avg_rating
FROM queries q
WHERE q.is_active = TRUE
GROUP BY DATE(q.created_at)
ORDER BY query_date DESC;
