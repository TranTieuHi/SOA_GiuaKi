export interface OTPRequest {
  user_id: string;
  email: string;
}

export interface OTPVerifyRequest extends OTPRequest {
  otp: string;
}

export interface OTPResponse {
  status: string;
  message: string;
  data: {
    user_id: string;
    email: string;
    otp?: string;
    expires_in?: number;
    verified?: boolean;
    txn_id?: string;
    timestamp: string;
  };
}

export interface OTPVerifyResponse {
  status: string;
  message: string;
  data: {
    user_id: string;
    email: string;
    verified: boolean;
    txn_id: string;
    timestamp: string;
  };
}

export interface OTPState {
  sent: boolean;
  sessionId: string;
  timeLeft: number;
  isLoading: boolean;
  error: string;
}

export interface OTPGenerateRequest {
  user_id: string;
  email: string;
}