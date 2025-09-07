#!/bin/bash

# NotebookLM RAG System Setup Script
# This script helps you set up the development environment quickly

set -e  # Exit on any error

echo "🚀 Setting up NotebookLM RAG System..."
echo "======================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command_exists python3; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

if ! command_exists docker; then
    echo "❌ Docker is required but not installed."
    exit 1
fi

if ! command_exists docker-compose; then
    echo "❌ Docker Compose is required but not installed."
    exit 1
fi

echo "✅ All prerequisites are installed."

# Create environment files
echo "📄 Creating environment files..."

if [ ! -f "backend/.env" ]; then
    if [ -f "backend/.env.example" ]; then
        cp backend/.env.example backend/.env
        echo "✅ Created backend/.env from template"
    else
        echo "⚠️  backend/.env.example not found, creating basic .env"
        cat > backend/.env << EOF
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/notebooklm_rag

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=./credentials/service-account.json
GOOGLE_CLOUD_PROJECT=your-project-id

# Redis
REDIS_URL=redis://localhost:6379

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO
EOF
    fi
else
    echo "✅ backend/.env already exists"
fi

if [ ! -f "frontend/.env.local" ]; then
    if [ -f "frontend/.env.example" ]; then
        cp frontend/.env.example frontend/.env.local
        echo "✅ Created frontend/.env.local from template"
    else
        echo "⚠️  frontend/.env.example not found, creating basic .env.local"
        cat > frontend/.env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=NotebookLM RAG System
NEXTAUTH_SECRET=your-nextauth-secret-change-this
NEXTAUTH_URL=http://localhost:3000
EOF
    fi
else
    echo "✅ frontend/.env.local already exists"
fi

# Create credentials directory
echo "📁 Creating credentials directory..."
mkdir -p backend/credentials

# Setup backend
echo "🐍 Setting up Python backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Backend setup complete"
cd ..

# Setup frontend
echo "⚛️  Setting up React frontend..."
cd frontend

echo "Installing Node.js dependencies..."
npm install

echo "✅ Frontend setup complete"
cd ..

# Setup database
echo "🗄️  Setting up database..."
if command_exists createdb; then
    createdb notebooklm_rag 2>/dev/null || echo "Database might already exist"
else
    echo "⚠️  PostgreSQL createdb not found. You may need to create the database manually."
fi

# Initialize database with schema
if command_exists psql; then
    echo "Initializing database schema..."
    psql -d notebooklm_rag -f database/init.sql 2>/dev/null || echo "Schema might already exist"
else
    echo "⚠️  PostgreSQL psql not found. You may need to initialize the database manually."
fi

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "🎯 Next steps:"
echo "1. Configure Google Cloud credentials:"
echo "   - Place your service account JSON file in backend/credentials/"
echo "   - Update GOOGLE_APPLICATION_CREDENTIALS in backend/.env"
echo ""
echo "2. Start the application:"
echo "   Option A - Docker (Recommended):"
echo "   $ docker-compose up -d"
echo ""
echo "   Option B - Local development:"
echo "   Terminal 1: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "   Terminal 2: cd frontend && npm run dev"
echo ""
echo "3. Access the application:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo ""
echo "🚀 Happy coding!"
