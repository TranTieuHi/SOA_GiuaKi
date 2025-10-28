// API Types để định nghĩa kiểu dữ liệu từ backend

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface User {
  user_id: string;
  username: string;
  full_name: string;
  email_address: string;
  phone_number: string;
  available_balance: number;
}

export interface LoginResponse {
  success: boolean;
  message: string;
  user?: User;
  session?: {
    loggedin: boolean;
  };
}

export interface ForgotPasswordRequest {
  email_address: string;
}

export interface ResetPasswordRequest {
  email_address: string;
  token: string;
  password: string;
  password_confirmation: string;
}

export interface APIResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
  error?: string;
}

// Request interceptor
tuitionApi.interceptors.request.use(
  (config) => {
    console.log('\n' + '='.repeat(60));
    console.log('📤 Outgoing Request:');
    console.log('   Method:', config.method?.toUpperCase());
    console.log('   Base URL:', config.baseURL);
    console.log('   URL:', config.url);
    console.log('   Full URL:', `${config.baseURL}${config.url}`);
    console.log('   Headers:', config.headers);
    console.log('   Params:', config.params);
    console.log('   Data:', config.data);
    console.log('='.repeat(60) + '\n');
    
    // ✅ Add Authorization header if token exists
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);