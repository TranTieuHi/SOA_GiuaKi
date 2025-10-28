import axios from 'axios';

// Environment variables
const AUTH_API_URL = import.meta.env.VITE_AUTH_API_URL || 'http://localhost:8000/api';
const TUITION_API_URL = import.meta.env.VITE_TUITION_API_URL || 'http://localhost:8001/api';
const OTP_API_URL = import.meta.env.VITE_OTP_API_URL || 'http://localhost:8002/api';

console.log('\n' + '='.repeat(70));
console.log('🔧 API CONFIGURATION');
console.log('='.repeat(70));
console.log('🔐 Auth API:', AUTH_API_URL);
console.log('💰 Tuition API:', TUITION_API_URL);
console.log('📧 OTP API:', OTP_API_URL);
console.log('='.repeat(70) + '\n');

// Create axios instances
export const authApi = axios.create({
  baseURL: AUTH_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

export const tuitionApi = axios.create({
  baseURL: TUITION_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

export const otpApi = axios.create({
  baseURL: OTP_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Request interceptor - Add token and log
const addAuthToken = (config: any) => {
  const token = localStorage.getItem('token');
  
  console.log('📤 Outgoing Request:');
  console.log('   Method:', config.method?.toUpperCase());
  console.log('   Base URL:', config.baseURL);
  console.log('   URL:', config.url);
  console.log('   Full URL:', `${config.baseURL}${config.url}`);
  console.log('   Params:', config.params || 'None');
  console.log('   Data:', config.data || 'None');
  
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
    console.log('   🔑 Token: Added');
  } else {
    console.log('   🔑 Token: Not present');
  }
  
  return config;
};

// Response interceptor - Handle errors and log
const handleResponse = (response: any) => {
  console.log('📥 Response Received:');
  console.log('   Status:', response.status);
  console.log('   URL:', response.config.url);
  console.log('   Data:', response.data);
  return response;
};

const handleResponseError = (error: any) => {
  console.error('\n' + '='.repeat(70));
  console.error('❌ API ERROR INTERCEPTOR');
  console.error('='.repeat(70));
  
  if (error.response) {
    console.error('📊 Response Details:');
    console.error('   Status:', error.response.status);
    console.error('   Status Text:', error.response.statusText);
    console.error('   URL:', error.config?.url);
    console.error('   Base URL:', error.config?.baseURL);
    console.error('   Method:', error.config?.method?.toUpperCase());
    console.error('   Data:', error.response.data);
    
    // Handle 401 Unauthorized
    if (error.response.status === 401) {
      console.warn('⚠️ Unauthorized - clearing token');
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      
      if (window.location.pathname !== '/login') {
        console.warn('⚠️ Redirecting to login...');
        window.location.href = '/login';
      }
    }
    
    // Handle 404 Not Found
    if (error.response.status === 404) {
      console.error('⚠️ Resource not found (404)');
      console.error('   Requested URL:', error.request?.responseURL || 'N/A');
      console.error('   Check if service is running on correct port');
    }
  } else if (error.request) {
    console.error('📡 Request Error (No Response):');
    console.error('   Message:', error.message);
    console.error('   Request URL:', error.config?.url);
    console.error('   Base URL:', error.config?.baseURL);
    console.error('   ⚠️ Service might not be running!');
  } else {
    console.error('⚠️ Setup Error:');
    console.error('   Message:', error.message);
  }
  
  console.error('='.repeat(70) + '\n');
  
  return Promise.reject(error);
};

// Apply interceptors
authApi.interceptors.request.use(addAuthToken);
authApi.interceptors.response.use(handleResponse, handleResponseError);

tuitionApi.interceptors.request.use(addAuthToken);
tuitionApi.interceptors.response.use(handleResponse, handleResponseError);

otpApi.interceptors.request.use(addAuthToken);
otpApi.interceptors.response.use(handleResponse, handleResponseError);

export default { authApi, tuitionApi, otpApi };