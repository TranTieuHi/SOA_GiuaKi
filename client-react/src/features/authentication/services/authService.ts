import { authApi } from '../../../services/api';
import { LoginRequest, LoginResponse, User } from '../../../types/auth';

export const login = async (credentials: LoginRequest): Promise<LoginResponse> => {
  try {
    console.log('🔄 Calling login API...');
    console.log('📤 Request:', { username: credentials.username, password: '***' });
    
    const response = await authApi.post<LoginResponse>('/auth/login', credentials);
    
    console.log('✅ Login API response:', response.data);
    
    const { user, token } = response.data;
    
    if (!token || !user) {
      throw new Error('Invalid response: missing token or user data');
    }
    
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
    
    console.log('✅ Token saved');
    console.log('✅ User saved:', user);
    
    return response.data;
  } catch (error: any) {
    console.error('❌ Login error:', error);
    
    // ✅ FIX: Parse error message correctly
    if (error.response) {
      const errorData = error.response.data;
      
      // Handle FastAPI error format
      if (errorData?.detail) {
        // If detail is object: { success: false, message: "...", error: "..." }
        if (typeof errorData.detail === 'object') {
          const message = errorData.detail.message || errorData.detail.error || 'Login failed';
          console.error('📛 Error details:', errorData.detail);
          throw new Error(message);
        }
        // If detail is string: "Not Found"
        else if (typeof errorData.detail === 'string') {
          throw new Error(errorData.detail);
        }
      }
      
      // Handle standard error format
      const message = errorData?.message || error.response.statusText || 'Login failed';
      throw new Error(message);
    }
    
    throw new Error(error.message || 'Login failed');
  }
};

export const logout = (): void => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  console.log('🔓 Logged out');
};

export const getCurrentUser = (): User | null => {
  const userStr = localStorage.getItem('user');
  if (!userStr) return null;
  
  try {
    return JSON.parse(userStr);
  } catch (error) {
    console.error('Error parsing user data:', error);
    return null;
  }
};

export const isAuthenticated = (): boolean => {
  return !!localStorage.getItem('token');
};

export const getToken = (): string | null => {
  return localStorage.getItem('token');
};