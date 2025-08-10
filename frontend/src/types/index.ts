// User types
export interface User {
  id: string;
  email: string;
  name: string;
  subscription_status: 'free' | 'premium' | 'enterprise';
  subscription_expires?: string;
  created_at: string;
  is_active: boolean;
  email_verified: boolean;
}

// Auth types
export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  name: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

// Chat types
export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  model_used?: string;
  tokens_used: number;
  cost_estimate: number;
  timestamp: string;
  processing_time?: number;
}

export interface Conversation {
  id: string;
  user_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  last_message_at: string;
  message_count: number;
  total_tokens: number;
  models_used: string[];
  tags: string[];
  category?: string;
  is_favorite: boolean;
  is_archived: boolean;
}

export interface ChatRequest {
  message: string;
  model?: string;
  temperature?: number;
  max_tokens?: number;
  stream?: boolean;
  conversation_id?: string;
  system_prompt?: string;
}

export interface ChatResponse {
  message: string;
  model_used: string;
  tokens_used: number;
  cost_estimate: number;
  conversation_id: string;
  timestamp: string;
  processing_time: number;
}

// LLM types
export interface LLMModel {
  provider: string;
  model: string;
  name: string;
  description: string;
  status: 'online' | 'offline' | 'maintenance';
  response_time_avg: number;
  error_rate: number;
  cost_per_1k_tokens: {
    input: number;
    output: number;
  };
  max_tokens: number;
  supports_streaming: boolean;
}

// Subscription types
export interface SubscriptionPlan {
  name: 'free' | 'premium' | 'enterprise';
  price: number;
  currency: string;
  interval: 'month' | 'year';
  features: {
    chat_requests_per_hour: number;
    tokens_per_day: number;
    available_llms: string[];
    history_retention_days: number | 'unlimited';
    export_formats: string[];
    priority_support: boolean;
    analytics?: boolean;
    custom_models?: boolean;
    api_access?: boolean;
  };
}

export interface Subscription {
  id: string;
  user_id: string;
  plan: string;
  status: 'active' | 'past_due' | 'canceled' | 'unpaid';
  current_period_start: string;
  current_period_end: string;
  cancel_at_period_end: boolean;
  stripe_subscription_id?: string;
  mercadopago_subscription_id?: string;
  payment_method: 'stripe' | 'mercadopago';
  created_at: string;
  updated_at: string;
}

// API Response types
export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

// UI types
export interface LoadingState {
  isLoading: boolean;
  message?: string;
}

export interface ErrorState {
  hasError: boolean;
  message?: string;
  code?: string;
}

// Theme types
export interface ThemeConfig {
  mode: 'light' | 'dark';
  primaryColor: string;
  fontFamily: string;
}
