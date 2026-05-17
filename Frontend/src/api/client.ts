import axios, { AxiosError, AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { API_CONFIG } from '@/config/api.config';
import { ApiError } from '@/types';

// Create axios instance with default config
const apiClient: AxiosInstance = axios.create({
  baseURL: API_CONFIG.baseURL,
  timeout: API_CONFIG.timeout,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Log request in development
    if (API_CONFIG.isDevelopment) {
      console.log('API Request:', {
        method: config.method?.toUpperCase(),
        url: config.url,
        params: config.params,
        data: config.data,
      });
    }
    
    return config;
  },
  (error) => {
    console.error('Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // Log response in development
    if (API_CONFIG.isDevelopment) {
      console.log('API Response:', {
        status: response.status,
        url: response.config.url,
        data: response.data,
      });
    }
    
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };
    
    // Handle specific error cases
    if (error.response) {
      const status = error.response.status;
      
      // Unauthorized - clear token and redirect to login
      if (status === 401) {
        localStorage.removeItem('auth_token');
        // Optionally redirect to login page
        // window.location.href = '/login';
      }
      
      // Retry logic for specific status codes
      if (
        API_CONFIG.retry.retryableStatuses.includes(status) &&
        !originalRequest._retry
      ) {
        originalRequest._retry = true;
        
        // Wait before retrying
        await new Promise((resolve) =>
          setTimeout(resolve, API_CONFIG.retry.retryDelay)
        );
        
        return apiClient(originalRequest);
      }
      
      // Format error response
      const apiError: ApiError = {
        message: error.response.data?.message || error.message || 'An error occurred',
        detail: error.response.data?.detail,
        status: status,
        errors: error.response.data?.errors,
      };
      
      console.error('API Error:', apiError);
      return Promise.reject(apiError);
    }
    
    // Network error
    if (error.request) {
      const networkError: ApiError = {
        message: 'Network error. Please check your connection.',
        status: 0,
      };
      console.error('Network Error:', networkError);
      return Promise.reject(networkError);
    }
    
    // Other errors
    const unknownError: ApiError = {
      message: error.message || 'An unknown error occurred',
      status: 0,
    };
    console.error('Unknown Error:', unknownError);
    return Promise.reject(unknownError);
  }
);

// Helper function to handle API calls with better error handling
export async function apiCall<T>(
  requestFn: () => Promise<AxiosResponse<T>>
): Promise<T> {
  try {
    const response = await requestFn();
    return response.data;
  } catch (error) {
    throw error;
  }
}

export default apiClient;

// Made with Bob
