export interface PaymentData {
  txId?: string;
  userId?: string;
  userAccountId?: string;
  mssv: string;
  studentName: string;
  studentClass: string;
  studentFaculty: string;
  dueAmount: number;
  availableBalance: number;
  remainingBalance: number;
  payerInfo: {
    name: string;
    email: string;
    phone: string;
  };
  studentData?: any;
  isValid: boolean;
  readyForPayment: boolean;
}

export interface PaymentResult {
  status: string;
  userId: string;
  oldBalance: number;
  newBalance: number;
  amountDeducted: number;
  receiptNo: string;
  timestamp: string;
  studentId: string;
  studentName: string;
  amount: number;
  payerName: string;
  payerEmail: string;
}

export interface PaymentRequest {
  user_id: string;
  student_id: string;
  amount: number;
}

export interface PaymentResponse {
  success: boolean;
  message: string;
  data: {
    user_id: string;
    student_id: string;
    amount: number;
    payment_date: string;
    user_info: {
      full_name: string;
      old_balance: number;
      new_balance: number;
      balance_deducted: number;
    };
  };
}

export interface PaymentHistoryItem {
  payment_id: number;
  user_id: string;
  student_id: string;
  amount_paid: number;
  payment_date: string;
  student_name: string;
  class: string;
  faculty: string;
  semester: string;
  year: number;
}

export interface PaymentHistoryResponse {
  success: boolean;
  total: number;
  limit: number;
  offset: number;
  data: PaymentHistoryItem[];
}

export interface PaymentStatistics {
  total_payments: number;
  total_amount: number;
  first_payment: string | null;
  last_payment: string | null;
}

export interface PaymentStatisticsResponse {
  success: boolean;
  data: PaymentStatistics;
}