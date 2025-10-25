import { useState } from 'react';
import { OTPService } from '../services/otpService';

export function useOTP() {
  const [otpSent, setOtpSent] = useState(false);
  const [otp, setOtp] = useState('');
  const [isSendingOtp, setIsSendingOtp] = useState(false);
  const [otpSessionId, setOtpSessionId] = useState('');
  const [error, setError] = useState('');

  const sendOTP = async (userId: string, email: string) => {
    setError('');
    setIsSendingOtp(true);

    try {
      // Step 1: Generate OTP
      const generateData = await OTPService.generateOTP({
        user_id: userId,
        email: email
      });

      if (generateData.status !== 'success') {
        throw new Error(generateData.message || 'Không thể tạo mã OTP');
      }

      // Step 2: Send OTP
      const sendData = await OTPService.sendOTP({
        user_id: generateData.data.user_id,
        email: generateData.data.email,
        otp: generateData.data.otp
      });

      if (sendData.status === 'success') {
        setOtpSent(true);
        setOtpSessionId(userId);
        console.log('✅ OTP sent successfully, session ID set to:', userId);
      } else {
        throw new Error(sendData.message || 'Không thể gửi mã OTP');
      }
    } catch (err: any) {
      console.error('❌ Send OTP error:', err);
      setError(err.message || 'Lỗi kết nối. Không thể gửi mã OTP.');
    } finally {
      setIsSendingOtp(false);
    }
  };

  const verifyOTP = async (email: string) => {
    if (otp.length !== 6) {
      setError('Vui lòng nhập đủ 6 chữ số mã OTP.');
      return null;
    }

    setError('');

    try {
      const otpData = await OTPService.verifyOTP({
        user_id: otpSessionId,
        email: email,
        otp: otp
      });

      if (otpData.status !== 'success') {
        if (otpData.httpStatus === 429) {
          setError('Quá nhiều lần thử. Vui lòng đợi 1 phút trước khi thử lại.');
        } else if (otpData.detail?.error === 'OTP expired') {
          setError('Mã OTP đã hết hạn. Vui lòng tạo mã mới.');
        } else {
          setError(otpData.detail?.message || otpData.detail || 'Mã OTP không đúng. Vui lòng thử lại.');
        }
        return null;
      }

      console.log('✅ OTP verified successfully');
      return otpData;
    } catch (err: any) {
      console.error('❌ OTP verification error:', err);
      setError(err.message || 'Lỗi xác thực OTP');
      return null;
    }
  };

  const resetOTP = () => {
    setOtpSent(false);
    setOtp('');
    setError('');
    setOtpSessionId('');
  };

  return {
    otpSent,
    otp,
    setOtp,
    isSendingOtp,
    otpSessionId,
    error,
    setError,
    sendOTP,
    verifyOTP,
    resetOTP
  };
}