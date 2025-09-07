// User types
export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  organization?: string;
  department?: string;
  bio?: string;
  is_active: boolean;
  is_admin: boolean;
  is_verified: boolean;
  notebook_id?: string;
  created_at: string;
  updated_at: string;
}

export interface UserCreate {
  username: string;
  email: string;
  full_name: string;
  password: string;
  organization?: string;
  department?: string;
  bio?: string;
}

export interface UserUpdate {
  full_name?: string;
  organization?: string;
  department?: string;
  bio?: string;
}

export interface UserLogin {
  username: string;
  password: string;
}

export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

// Document types
export interface Document {
  id: number;
  filename: string;
  original_filename: string;
  file_size: number;
  file_type: string;
  mime_type: string;
  title?: string;
  description?: string;
  content_preview?: string;
  metadata?: Record<string, any>;
  notebooklm_document_id?: string;
  processing_status: 'pending' | 'processing' | 'completed' | 'failed';
  processing_error?: string;
  query_count: number;
  last_queried_at?: string;
  owner_id: number;
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

export interface DocumentUpload {
  id: number;
  filename: string;
  original_filename: string;
  file_size: number;
  processing_status: string;
  message: string;
}

export interface DocumentList {
  documents: Document[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface DocumentStats {
  total_documents: number;
  total_size: number;
  by_file_type: Record<string, number>;
  by_status: Record<string, number>;
  recent_uploads: Document[];
}

// Query types
export interface Query {
  id: number;
  query_text: string;
  query_type: 'semantic' | 'keyword' | 'conversational';
  response_text?: string;
  response_sources?: QuerySource[];
  response_metadata?: Record<string, any>;
  execution_time?: number;
  tokens_used?: number;
  status: 'pending' | 'completed' | 'failed';
  error_message?: string;
  conversation_id?: string;
  parent_query_id?: number;
  context?: Record<string, any>;
  user_rating?: number;
  user_feedback?: string;
  relevance_score?: number;
  user_id: number;
  created_at: string;
  updated_at: string;
}

export interface QuerySource {
  document_id: string;
  document_name: string;
  excerpt: string;
  page_number?: number;
  relevance_score?: number;
}

export interface QueryExecution {
  query_text: string;
  include_sources?: boolean;
  max_results?: number;
  conversation_id?: string;
  context?: Record<string, any>;
}

export interface QueryResult {
  query_id: number;
  query_text: string;
  response_text: string;
  sources: QuerySource[];
  metadata: Record<string, any>;
  execution_time: number;
  conversation_id?: string;
  status: string;
}

export interface ConversationHistory {
  conversation_id: string;
  queries: Query[];
  total_queries: number;
  started_at: string;
  last_activity: string;
}

export interface QueryStats {
  total_queries: number;
  successful_queries: number;
  failed_queries: number;
  average_execution_time: number;
  average_rating?: number;
  popular_queries: string[];
  recent_queries: Query[];
}

// API types
export interface ApiResponse<T = any> {
  data?: T;
  message?: string;
  error?: string;
  status: number;
}

export interface PaginatedResponse<T = any> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// Form types
export interface LoginFormData {
  username: string;
  password: string;
}

export interface RegisterFormData {
  username: string;
  email: string;
  full_name: string;
  password: string;
  confirm_password: string;
  organization?: string;
  department?: string;
  bio?: string;
}

export interface QueryFormData {
  query_text: string;
  include_sources: boolean;
  max_results: number;
}

// UI types
export interface AlertProps {
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  title?: string;
  onClose?: () => void;
}

export interface LoadingState {
  isLoading: boolean;
  error?: string;
}

export interface TableColumn {
  key: string;
  title: string;
  sortable?: boolean;
  render?: (value: any, record: any) => React.ReactNode;
}

// Theme types
export type ThemeMode = 'light' | 'dark' | 'system';

// Navigation types
export interface NavigationItem {
  label: string;
  href: string;
  icon?: React.ComponentType;
  badge?: string | number;
  children?: NavigationItem[];
}

// Settings types
export interface UserSettings {
  theme: ThemeMode;
  language: string;
  notifications: {
    email: boolean;
    push: boolean;
    query_results: boolean;
    document_processing: boolean;
  };
  privacy: {
    profile_visibility: 'public' | 'private';
    query_history: 'keep' | 'delete_after_30_days' | 'delete_after_90_days';
  };
}
