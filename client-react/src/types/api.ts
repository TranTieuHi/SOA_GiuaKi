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