import { useState } from 'react';
import { PaymentService } from '../services/paymentService';
import { PaymentData, PaymentResult, PaymentRequest } from '../types/payment';

export function usePayment() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState('');

  const processPayment = async (
    paymentData: PaymentData,
    userId: string
  ): Promise<PaymentResult | null> => {
    setIsProcessing(true);
    setError('');

    try {
      const paymentRequest: PaymentRequest = {
        user_id: userId,
        student_id: paymentData.mssv,
        amount: paymentData.dueAmount
      };

      const paymentResponse = await PaymentService.processPayment(paymentRequest);

      const result: PaymentResult = {
        status: 'SUCCESS',
        userId: userId,
        oldBalance: paymentResponse.data.user_info.old_balance,
        newBalance: paymentResponse.data.user_info.new_balance,
        amountDeducted: paymentResponse.data.user_info.balance_deducted,
        receiptNo: `RCP_${Date.now()}`,
        timestamp: paymentResponse.data.payment_date,
        studentId: paymentData.mssv,
        studentName: paymentData.studentName,
        amount: paymentData.dueAmount,
        payerName: paymentResponse.data.user_info.full_name,
        payerEmail: paymentData.payerInfo?.email
      };

      console.log('🎉 Payment completed successfully:', result);
      return result;

    } catch (err) {
      console.error('❌ Payment processing error:', err);
      const errorMessage = err instanceof Error ? err.message : 'Lỗi xử lý thanh toán';
      setError(errorMessage);
      return null;
    } finally {
      setIsProcessing(false);
    }
  };

  return {
    processPayment,
    isProcessing,
    error,
    setError
  };
}