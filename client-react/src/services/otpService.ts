import axios from 'axios';
import { OTPGenerateRequest, OTPVerifyRequest, OTPResponse } from '../types/otp';

const OTP_API_URL = import.meta.env.VITE_OTP_API_URL || 'http://localhost:8002/api';

const otpApi = axios.create({
  baseURL: OTP_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Generate OTP
export const generateOTP = async (data: OTPGenerateRequest): Promise<OTPResponse> => {
  try {
    const response = await otpApi.post('/otp/generate', data);
    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.message || 'Failed to generate OTP');
  }
};

// Send OTP via email
export const sendOTP = async (data: { user_id: string; email: string; otp: string }): Promise<OTPResponse> => {
  try {
    const response = await otpApi.post('/otp/send', data);
    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.message || 'Failed to send OTP');
  }
};

// Verify OTP
export const verifyOTP = async (data: OTPVerifyRequest): Promise<OTPResponse> => {
  try {
    const response = await otpApi.post('/otp/verify', data);
    return response.data;
  } catch (error: any) {
    const errorDetail = error.response?.data?.detail;
    if (errorDetail?.error) {
      throw new Error(errorDetail.message || errorDetail.error);
    }
    throw new Error(error.response?.data?.message || 'Failed to verify OTP');
  }
};