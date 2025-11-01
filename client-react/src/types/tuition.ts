// Student types
export interface Student {
  student_id: string;
  full_name: string;
  class: string;
  faculty: string;
  tuition_amount: number;
  is_payed: boolean;
  created_at?: string;
}

export interface StudentListResponse {
  students: Student[];
  total_count: number;
  total_unpaid_amount: number;
  unpaid_count: number;
}

// Payment types
export interface PaymentRequest {
  student_id: string;
}

export interface PaymentResponse {
  success: boolean;
  statusCode: number;
  message: string;
  data: {
    payment_id: number;
    student_id: string;
    student_name: string;
    student_class: string;
    student_faculty: string;
    amount_paid: number;
    payment_date: string;
    remaining_balance: number;
  };
}

export interface PaymentHistoryItem {
  payment_id: number;
  student_id: string;
  student_name: string;
  student_class: string;
  student_faculty: string;
  semester: string;
  year: number;
  amount: number;
  payment_date: string;
  user_id: string;
  username: string;
  user_full_name: string;
}

export interface PaymentHistoryResponse {
  payments: PaymentHistoryItem[];
  total_count: number;
  total_amount: number;
}

// API Error Response
export interface TuitionErrorResponse {
  detail: {
    success: boolean;
    statusCode: number;
    message: string;
    error: string;
  } | string;
}