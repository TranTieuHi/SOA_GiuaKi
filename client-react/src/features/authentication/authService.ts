// filepath: client-react/src/features/authentication/authService.ts
import axios from 'axios';

const AUTH_API_URL = import.meta.env.VITE_AUTH_API_URL || 'http://localhost:8000/api';

interface LoginRequest {
  username: string;
  password: string;
}

interface LoginResponse {
  success: boolean;
  statusCode: number;
  message: string;
  token: string;
  user: {
    user_id: string;
    username: string;
    email_address: string;
    full_name: string;
    available_balance: number;
  };
}

/**
 * Hàm đăng nhập
 * Gửi thông tin đăng nhập đến FastAPI Auth Service và lưu token vào localStorage
 */
export const login = async (credentials: LoginRequest): Promise<LoginResponse> => {
  try {
    const response = await axios.post<LoginResponse>(`${AUTH_API_URL}/auth/login`, credentials);
    
    console.log('✅ Login response:', response.data);
    
    // ✅ FIX: Response structure là response.data (không có .data.data)
    const { user, token } = response.data;
    
    // Validate token và user
    if (!token || !user) {
      throw new Error('Invalid response: missing token or user data');
    }
    
    // LƯU TOKEN VÀ USER VÀO LOCALSTORAGE
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
    
    console.log('✅ Token saved:', token.substring(0, 50) + '...');
    console.log('✅ User saved:', user);
    
    return response.data;
  } catch (error: any) {
    console.error('❌ Login error:', error);
    
    // Handle axios error
    if (error.response) {
      const message = error.response.data?.message || 'Login failed';
      throw new Error(message);
    }
    
    throw new Error(error.message || 'Login failed');
  }
};

/**
 * Hàm đăng xuất
 */
export const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  console.log('🔓 Logged out, token cleared');
};

/**
 * Hàm lấy thông tin user hiện tại từ localStorage
 */
export const getCurrentUser = () => {
  const userStr = localStorage.getItem('user');
  if (!userStr) return null;
  
  try {
    return JSON.parse(userStr);
  } catch (error) {
    console.error('Error parsing user data:', error);
    return null;
  }
};

/**
 * Hàm kiểm tra xem user đã đăng nhập chưa
 */
export const isAuthenticated = (): boolean => {
  const token = localStorage.getItem('token');
  const hasToken = !!token;
  console.log('🔐 isAuthenticated check:', hasToken);
  return hasToken;
};

/**
 * Hàm lấy token hiện tại
 */
export const getToken = (): string | null => {
  return localStorage.getItem('token');
};