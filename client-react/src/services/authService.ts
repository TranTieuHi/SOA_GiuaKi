import { authApi } from './api';

export interface User {
  user_id: string;
  username: string;
  email_address: string;
  full_name: string;
  phone_number?: string;
  available_balance: number;
  created_at?: string;
  updated_at?: string;
}

export interface UserProfile {
  user_id: string;
  username: string;
  email_address: string;
  full_name: string;
  phone_number?: string;
  available_balance: number;
  created_at: string;
  updated_at: string;
}

export interface LoginResponse {
  success: boolean;
  statusCode: number;
  message: string;
  token: string;
  user: User;
}

// ✅ LOGIN FUNCTION
export const login = async (credentials: { username: string; password: string }): Promise<LoginResponse> => {
  try {
    console.log('\n' + '='.repeat(60));
    console.log('🔐 LOGGING IN');
    console.log('='.repeat(60));
    console.log('Username:', credentials.username);
    
    const response = await authApi.post('/auth/login', credentials);
    
    console.log('✅ Login response:', response.data);
    console.log('='.repeat(60) + '\n');
    
    if (response.data.success) {
      // Store token and user data
      localStorage.setItem('token', response.data.token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
      
      return response.data;
    }
    
    throw new Error(response.data.message || 'Login failed');
  } catch (error) {
    console.error('❌ Login error:', error);
    throw error;
  }
};

// ✅ GET USER PROFILE FROM API
export const getUserProfile = async (): Promise<UserProfile> => {
  try {
    console.log('\n' + '='.repeat(60));
    console.log('👤 GETTING USER PROFILE');
    console.log('='.repeat(60));
    
    const response = await authApi.get('/auth/profile');
    
    console.log('✅ Profile response:', response.data);
    console.log('='.repeat(60) + '\n');
    
    return response.data.user;
  } catch (error) {
    console.error('❌ Get profile error:', error);
    throw error;
  }
};

// ✅ REFRESH USER DATA (Update localStorage with fresh data from API)
export const refreshUserData = async (): Promise<User> => {
  try {
    console.log('\n' + '='.repeat(60));
    console.log('🔄 REFRESHING USER DATA');
    console.log('='.repeat(60));
    
    const response = await authApi.get('/auth/profile');
    
    console.log('✅ Profile API response:', response.data);
    console.log('📊 Profile response balance:', response.data.user?.available_balance);
    
    const userData = response.data.user;
    
    // ✅ Log before and after localStorage update
    const oldUser = getCurrentUser();
    console.log('🔄 Old balance in localStorage:', oldUser?.available_balance);
    console.log('🆕 New balance from API:', userData.available_balance);
    
    // Update localStorage with fresh data
    localStorage.setItem('user', JSON.stringify(userData));
    
    // Verify localStorage was updated
    const updatedUser = getCurrentUser();
    console.log('✅ Updated balance in localStorage:', updatedUser?.available_balance);
    
    console.log('📱 User data updated in localStorage');
    console.log('='.repeat(60) + '\n');
    
    return userData;
  } catch (error) {
    console.error('❌ Refresh user data error:', error);
    throw error;
  }
};

// ✅ GET CURRENT USER FROM LOCALSTORAGE
export const getCurrentUser = (): User | null => {
  try {
    const userStr = localStorage.getItem('user');
    if (!userStr) return null;
    
    const user = JSON.parse(userStr);
    return user;
  } catch (error) {
    console.error('Error parsing user data:', error);
    return null;
  }
};

// ✅ LOGOUT
export const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  console.log('🚪 User logged out');
};

// ✅ CHECK AUTHENTICATION STATUS
export const isAuthenticated = (): boolean => {
  const token = localStorage.getItem('token');
  const user = localStorage.getItem('user');
  return !!(token && user);
};

// ✅ REGISTER USER
export const register = async (userData: {
  username: string;
  email_address: string;
  password: string;
  full_name: string;
  phone_number?: string;
}) => {
  try {
    console.log('\n' + '='.repeat(60));
    console.log('📝 REGISTERING USER');
    console.log('='.repeat(60));
    console.log('Username:', userData.username);
    console.log('Email:', userData.email_address);
    
    const response = await authApi.post('/auth/register', userData);
    
    console.log('✅ Register response:', response.data);
    console.log('='.repeat(60) + '\n');
    
    return response.data;
  } catch (error) {
    console.error('❌ Register error:', error);
    throw error;
  }
};

// ✅ UPDATE USER BALANCE (Called after successful payment)
export const updateUserBalance = (newBalance: number) => {
  try {
    const user = getCurrentUser();
    if (user) {
      user.available_balance = newBalance;
      localStorage.setItem('user', JSON.stringify(user));
      console.log('💰 Balance updated in localStorage:', newBalance.toLocaleString('vi-VN'));
    }
  } catch (error) {
    console.error('❌ Error updating user balance:', error);
  }
};

// ✅ GET TOKEN
export const getToken = (): string | null => {
  return localStorage.getItem('token');
};

// ✅ VALIDATE TOKEN (Check if token exists and user is logged in)
export const validateSession = async (): Promise<boolean> => {
  try {
    if (!isAuthenticated()) {
      return false;
    }
    
    // Try to get profile to validate token
    await getUserProfile();
    return true;
  } catch (error) {
    console.error('❌ Session validation failed:', error);
    // Clear invalid session
    logout();
    return false;
  }
};