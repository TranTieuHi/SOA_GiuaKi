import axios from 'axios';
import { PaymentHistoryResponse, PaymentStatisticsResponse } from '../types/payment';

const TUITION_API_URL = import.meta.env.VITE_TUITION_API_URL || 'http://localhost:8001/api';

const getAuthToken = () => {
  const token = localStorage.getItem('token');
  console.log('🔑 Getting token from localStorage:', token ? 'Found' : 'Not found');
  console.log('🔑 Token length:', token?.length);
  return token;
};

const paymentApi = axios.create({
  baseURL: TUITION_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ✅ Add token to requests
paymentApi.interceptors.request.use((config) => {
  const token = getAuthToken();
  
  console.log('📤 Making request to:', config.url);
  console.log('🔑 Token available:', token ? 'Yes' : 'No');
  
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
    console.log('✅ Authorization header set');
  } else {
    console.warn('⚠️ No token found in localStorage!');
  }
  
  console.log('📋 Request headers:', config.headers);
  return config;
});

// ✅ Add response interceptor
paymentApi.interceptors.response.use(
  (response) => {
    console.log('✅ Response received:', response.status);
    console.log('📦 Response data:', response.data);
    return response;
  },
  (error) => {
    console.error('❌ Request failed:', error.response?.status);
    console.error('❌ Error detail:', error.response?.data);
    console.error('❌ Error message:', error.message);
    return Promise.reject(error);
  }
);

export const getPaymentHistory = async (
  limit: number = 50,
  offset: number = 0
): Promise<PaymentHistoryResponse> => {
  try {
    console.log('🔄 Fetching payment history...');
    const response = await paymentApi.get('/payments/history', {
      params: { limit, offset }
    });
    return response.data;
  } catch (error: any) {
    console.error('❌ getPaymentHistory error:', error);
    throw new Error(error.response?.data?.detail || 'Failed to get payment history');
  }
};

export const getPaymentStatistics = async (): Promise<PaymentStatisticsResponse> => {
  try {
    console.log('🔄 Fetching payment statistics...');
    const response = await paymentApi.get('/payments/statistics');
    return response.data;
  } catch (error: any) {
    console.error('❌ getPaymentStatistics error:', error);
    throw new Error(error.response?.data?.detail || 'Failed to get statistics');
  }
};