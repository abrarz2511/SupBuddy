// Generic API response wrapper
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: number;
}

// Paginated response
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
  has_more: boolean;
}

// API Error response
export interface ApiError {
  message: string;
  detail?: string;
  status: number;
  errors?: Record<string, string[]>;
}

// Common query parameters
export interface PaginationParams {
  skip?: number;
  limit?: number;
}

export interface DateRangeParams {
  from_date?: string;
  to_date?: string;
}

// API request configuration
export interface ApiRequestConfig {
  timeout?: number;
  retries?: number;
  retryDelay?: number;
}

// Made with Bob
