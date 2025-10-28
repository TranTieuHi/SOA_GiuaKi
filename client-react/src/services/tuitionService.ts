import { tuitionApi } from './api';

export interface Student {
  student_id: string;
  full_name: string;
  class: string;
  faculty: string;
  semester: string;
  year: number;  // ✅ Changed from academic_year: string to year: number
  tuition_amount: number;
  is_payed: boolean;
  created_at: string | null;
  version: number;
}

export interface SearchStudentResponse {
  success: boolean;
  statusCode: number;
  message: string;
  data: Student;
}

export const searchStudent = async (studentId: string): Promise<Student> => {
  try {
    console.log('\n' + '='.repeat(60));
    console.log('🔍 SEARCH STUDENT REQUEST');
    console.log('='.repeat(60));
    console.log('📝 Student ID:', studentId);
    console.log('🌐 API Base URL:', tuitionApi.defaults.baseURL);
    console.log('🔗 Full URL:', `${tuitionApi.defaults.baseURL}/students/search?student_id=${studentId}`);
    console.log('='.repeat(60));
    
    const response = await tuitionApi.get<SearchStudentResponse>(
      '/students/search',
      {
        params: { student_id: studentId }
      }
    );
    
    console.log('✅ RESPONSE RECEIVED');
    console.log('   Status:', response.status);
    console.log('   Data:', response.data);
    console.log('='.repeat(60) + '\n');
    
    if (!response.data.success) {
      throw new Error(response.data.message || 'Search failed');
    }
    
    return response.data.data;
  } catch (error: any) {
    console.error('\n' + '='.repeat(60));
    console.error('❌ SEARCH STUDENT ERROR');
    console.error('='.repeat(60));
    
    if (error.response) {
      console.error('📊 Response Error:');
      console.error('   Status:', error.response.status);
      console.error('   Status Text:', error.response.statusText);
      console.error('   Data:', error.response.data);
      console.error('   Headers:', error.response.headers);
      console.error('   Config URL:', error.config?.url);
      console.error('   Config Base URL:', error.config?.baseURL);
      console.error('   Full Request URL:', error.request?.responseURL || 'N/A');
    } else if (error.request) {
      console.error('📡 Request Error (No Response):');
      console.error('   Request:', error.request);
      console.error('   Message:', error.message);
    } else {
      console.error('⚠️ Setup Error:');
      console.error('   Message:', error.message);
    }
    
    console.error('   Error Code:', error.code);
    console.error('   Error Name:', error.name);
    console.error('='.repeat(60) + '\n');
    
    throw error;
  }
};

export const getAllStudents = async (): Promise<Student[]> => {
  try {
    const response = await tuitionApi.get<{success: boolean; data: Student[]}>('/students/');
    return response.data.data;
  } catch (error) {
    console.error('❌ Get all students error:', error);
    throw error;
  }
};

export const getUnpaidStudents = async (): Promise<Student[]> => {
  try {
    const response = await tuitionApi.get<{success: boolean; data: Student[]}>('/students/unpaid');
    return response.data.data;
  } catch (error) {
    console.error('❌ Get unpaid students error:', error);
    throw error;
  }
};

export const payTuition = async (paymentData: any) => {
  try {
    console.log('💳 Paying tuition:', paymentData);
    const response = await tuitionApi.post('/payments/pay', paymentData);
    console.log('✅ Payment response:', response.data);
    return response.data;
  } catch (error) {
    console.error('❌ Payment error:', error);
    throw error;
  }
};

export const getPaymentHistory = async (userId: string) => {
  try {
    console.log('📋 Getting payment history for user:', userId);
    const response = await tuitionApi.get(`/payments/history?user_id=${userId}`);
    console.log('✅ Payment history:', response.data);
    return response.data;
  } catch (error) {
    console.error('❌ Payment history error:', error);
    throw error;
  }
};