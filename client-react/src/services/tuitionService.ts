import apiClient from './apiClient';
import { Student, StudentListResponse, PaymentRequest, PaymentResponse, PaymentHistoryResponse } from '../types/tuition';

const TUITION_API_BASE = 'http://localhost:8001/api';

// Tạo axios instance riêng cho Tuition Service
const tuitionClient = apiClient.create({
  baseURL: TUITION_API_BASE,
});

// Copy interceptors từ apiClient
tuitionClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

/**
 * Tìm kiếm sinh viên theo student_id
 */
export const searchStudent = async (studentId: string): Promise<Student> => {
  try {
    console.log(`🔍 Searching for student: ${studentId}`);
    const response = await tuitionClient.get<Student>(`/students/search`, {
      params: { student_id: studentId }
    });
    console.log('✅ Student found:', response.data);
    return response.data;
  } catch (error: any) {
    console.error('❌ Error searching student:', error);
    
    if (error.response) {
      const { status, data } = error.response;
      const errorDetail = data.detail || data;
      
      switch (status) {
        case 404:
          throw new Error(errorDetail.message || 'Không tìm thấy sinh viên');
        case 401:
          throw new Error('Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.');
        default:
          throw new Error(errorDetail.message || 'Lỗi tìm kiếm sinh viên');
      }
    }
    
    throw new Error('Không thể kết nối đến Tuition Service');
  }
};

/**
 * Lấy danh sách tất cả sinh viên
 */
export const getAllStudents = async (): Promise<StudentListResponse> => {
  try {
    const response = await tuitionClient.get<StudentListResponse>('/students/');
    return response.data;
  } catch (error: any) {
    console.error('❌ Error getting all students:', error);
    throw new Error(error.response?.data?.detail?.message || 'Lỗi lấy danh sách sinh viên');
  }
};

/**
 * Lấy danh sách sinh viên chưa thanh toán
 */
export const getUnpaidStudents = async (): Promise<StudentListResponse> => {
  try {
    const response = await tuitionClient.get<StudentListResponse>('/students/unpaid');
    return response.data;
  } catch (error: any) {
    console.error('❌ Error getting unpaid students:', error);
    throw new Error(error.response?.data?.detail?.message || 'Lỗi lấy danh sách sinh viên chưa thanh toán');
  }
};

/**
 * Thanh toán học phí
 */
export const payTuition = async (paymentData: PaymentRequest): Promise<PaymentResponse> => {
  try {
    console.log('💳 Processing payment for student:', paymentData.student_id);
    const response = await tuitionClient.post<PaymentResponse>('/payments/pay', paymentData);
    console.log('✅ Payment successful:', response.data);
    return response.data;
  } catch (error: any) {
    console.error('❌ Payment error:', error);
    
    if (error.response) {
      const { status, data } = error.response;
      const errorDetail = data.detail || data;
      
      switch (status) {
        case 400:
          throw new Error(errorDetail.message || 'Dữ liệu thanh toán không hợp lệ');
        case 404:
          throw new Error(errorDetail.message || 'Không tìm thấy sinh viên');
        case 401:
          throw new Error('Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.');
        default:
          throw new Error(errorDetail.message || 'Thanh toán thất bại');
      }
    }
    
    throw new Error('Không thể kết nối đến Tuition Service');
  }
};

/**
 * Lấy lịch sử thanh toán của user
 */
export const getPaymentHistory = async (): Promise<PaymentHistoryResponse> => {
  try {
    const response = await tuitionClient.get<PaymentHistoryResponse>('/payments/history');
    return response.data;
  } catch (error: any) {
    console.error('❌ Error getting payment history:', error);
    throw new Error(error.response?.data?.detail?.message || 'Lỗi lấy lịch sử thanh toán');
  }
};

/**
 * Lấy tất cả lịch sử thanh toán (Admin)
 */
export const getAllPayments = async (): Promise<PaymentHistoryResponse> => {
  try {
    const response = await tuitionClient.get<PaymentHistoryResponse>('/payments/all');
    return response.data;
  } catch (error: any) {
    console.error('❌ Error getting all payments:', error);
    throw new Error(error.response?.data?.detail?.message || 'Lỗi lấy lịch sử thanh toán');
  }
};