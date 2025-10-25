import axios from 'axios';
import type { 
  LoginCredentials, 
  LoginResponse, 
  ForgotPasswordRequest, 
  ResetPasswordRequest,
  APIResponse 
} from '../types/api';

// Base URLs
const API_BASE_URL = 'http://localhost:4000';
const OTP_SERVICE_URL = 'http://localhost:8000';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important for session cookies
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    console.log('🔄 API Request:', config.method?.toUpperCase(), config.url, config.data);
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    console.log('✅ API Response:', response.status, response.data);
    return response;
  },
  (error) => {
    console.error('❌ API Error:', error.response?.status, error.response?.data);
    
    // Handle specific error cases
    if (error.response?.status === 400) {
      throw new Error(error.response.data?.message || 'Bad request');
    } else if (error.response?.status === 401) {
      throw new Error('Invalid credentials');
    } else if (error.response?.status === 500) {
      throw new Error('Server error. Please try again later.');
    } else if (error.code === 'ECONNREFUSED') {
      throw new Error('Cannot connect to server. Please check if backend is running.');
    }
    
    return Promise.reject(error);
  }
);

// Auth API calls
export const authAPI = {
  // Login
  login: async (credentials: LoginCredentials): Promise<LoginResponse> => {
    try {
      console.log('🔑 Attempting login for:', credentials.email);
      const response = await apiClient.post('/auth/login', credentials);
      return response.data;
    } catch (error: any) {
      console.error('❌ Login failed:', error.message);
      throw error;
    }
  },

  // Logout
  logout: async (): Promise<APIResponse> => {
    try {
      const response = await apiClient.post('/auth/logout');
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Logout failed');
    }
  },

  // Forgot Password
  forgotPassword: async (data: ForgotPasswordRequest): Promise<APIResponse> => {
    try {
      const response = await apiClient.post('/password/forgot', data);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Request failed');
    }
  },

  // Reset Password
  resetPassword: async (data: ResetPasswordRequest): Promise<APIResponse> => {
    try {
      const response = await apiClient.post('/password/reset', data);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Reset failed');
    }
  },

  // Check reset token
  checkResetToken: async (email: string, token: string): Promise<APIResponse> => {
    try {
      const response = await apiClient.get(`/password/check-token/${email}/${token}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Token validation failed');
    }
  }
};

// OTP API calls
export const otpAPI = {
  // Generate OTP
  generateOTP: async (userId: string, email: string): Promise<APIResponse> => {
    try {
      const response = await apiClient.post('/otp/generate', {
        userId,
        email
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'OTP generation failed');
    }
  },

  // Verify OTP
  verifyOTP: async (userId: string, email: string, otp: string): Promise<APIResponse> => {
    try {
      const response = await apiClient.post('/otp/verify', {
        userId,
        email,
        otp
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'OTP verification failed');
    }
  }
};

export default apiClient;