import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import toast from 'react-hot-toast';

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_TIMEOUT = parseInt(process.env.NEXT_PUBLIC_API_TIMEOUT || '30000');

// Types
interface ApiError {
  detail: string;
  error_type?: string;
  correlation_id?: string;
}

interface ApiRequestConfig extends AxiosRequestConfig {
  skipAuth?: boolean;
  skipErrorHandling?: boolean;
}

class ApiClient {
  private client: AxiosInstance;
  private authToken: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: API_TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
    this.loadAuthToken();
  }

  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add auth token if available and not skipped
        if (this.authToken && !config.skipAuth) {
          config.headers.Authorization = `Bearer ${this.authToken}`;
        }

        // Add correlation ID for request tracking
        config.headers['X-Correlation-ID'] = this.generateCorrelationId();

        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        return response;
      },
      async (error) => {
        const config = error.config as ApiRequestConfig;

        // Handle token expiration
        if (error.response?.status === 401 && !config.skipAuth) {
          await this.handleTokenExpiration();
          return;
        }

        // Handle errors if not skipped
        if (!config.skipErrorHandling) {
          this.handleApiError(error);
        }

        return Promise.reject(error);
      }
    );
  }

  private generateCorrelationId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  private loadAuthToken() {
    if (typeof window !== 'undefined') {
      this.authToken = localStorage.getItem('access_token');
    }
  }

  private saveAuthToken(token: string) {
    this.authToken = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', token);
    }
  }

  private clearAuthToken() {
    this.authToken = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  }

  private async handleTokenExpiration() {
    try {
      const refreshToken = typeof window !== 'undefined' 
        ? localStorage.getItem('refresh_token') 
        : null;

      if (!refreshToken) {
        this.clearAuthToken();
        window.location.href = '/auth/login';
        return;
      }

      const response = await this.client.post('/api/v1/auth/refresh', {
        refresh_token: refreshToken,
      }, { skipAuth: true });

      const { access_token, refresh_token: newRefreshToken } = response.data;
      this.saveAuthToken(access_token);
      
      if (typeof window !== 'undefined') {
        localStorage.setItem('refresh_token', newRefreshToken);
      }

    } catch (error) {
      this.clearAuthToken();
      toast.error('Session expired. Please log in again.');
      window.location.href = '/auth/login';
    }
  }

  private handleApiError(error: any) {
    let message = 'An unexpected error occurred';

    if (error.response) {
      const apiError: ApiError = error.response.data;
      message = apiError.detail || message;

      // Log error details for debugging
      console.error('API Error:', {
        status: error.response.status,
        data: error.response.data,
        url: error.config?.url,
        method: error.config?.method,
      });

      // Show user-friendly error messages
      switch (error.response.status) {
        case 400:
          toast.error(`Validation Error: ${message}`);
          break;
        case 401:
          toast.error('Authentication required');
          break;
        case 403:
          toast.error('Permission denied');
          break;
        case 404:
          toast.error('Resource not found');
          break;
        case 429:
          toast.error('Too many requests. Please try again later.');
          break;
        case 500:
          toast.error('Server error. Please try again later.');
          break;
        default:
          toast.error(message);
      }
    } else if (error.request) {
      console.error('Network Error:', error.request);
      toast.error('Network error. Please check your connection.');
    } else {
      console.error('Error:', error.message);
      toast.error(message);
    }
  }

  // Public methods
  public setAuthToken(token: string) {
    this.saveAuthToken(token);
  }

  public clearAuth() {
    this.clearAuthToken();
  }

  public async get<T = any>(url: string, config?: ApiRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.client.get(url, config);
    return response.data;
  }

  public async post<T = any>(url: string, data?: any, config?: ApiRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.client.post(url, data, config);
    return response.data;
  }

  public async put<T = any>(url: string, data?: any, config?: ApiRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.client.put(url, data, config);
    return response.data;
  }

  public async patch<T = any>(url: string, data?: any, config?: ApiRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.client.patch(url, data, config);
    return response.data;
  }

  public async delete<T = any>(url: string, config?: ApiRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.client.delete(url, config);
    return response.data;
  }

  // File upload method
  public async uploadFile<T = any>(
    url: string,
    file: File,
    data?: Record<string, any>,
    onUploadProgress?: (progressEvent: any) => void
  ): Promise<T> {
    const formData = new FormData();
    formData.append('file', file);

    if (data) {
      Object.keys(data).forEach(key => {
        formData.append(key, data[key]);
      });
    }

    const response: AxiosResponse<T> = await this.client.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    });

    return response.data;
  }
}

// Create and export singleton instance
export const apiClient = new ApiClient();

// Utility functions
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const formatRelativeTime = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffInSeconds < 60) return 'Just now';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
  if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)} days ago`;

  return formatDate(dateString);
};

export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const validatePassword = (password: string): boolean => {
  // At least 8 characters, 1 uppercase, 1 lowercase, 1 number
  const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/;
  return passwordRegex.test(password);
};

export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void => {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};

export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength).trim() + '...';
};
