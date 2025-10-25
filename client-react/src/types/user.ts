/**
 * Định nghĩa cấu trúc dữ liệu cho một đối tượng người dùng,
 * tương ứng với các trường trong database.
 *
 * Lưu ý: Trường `password` không bao giờ được gửi từ backend về frontend
 * để đảm bảo an toàn.
 */
export interface User {
  user_id: string;
  username: string;
  email_address: string;
  full_name: string;
  phone_number: string | null;
  available_balance: number; // decimal(12,2) trong SQL tương ứng với kiểu number trong TypeScript
}

/**
 * Kiểu dữ liệu cho phản hồi từ API khi đăng nhập thành công.
 * API sẽ trả về một token để xác thực và thông tin người dùng (không bao gồm mật khẩu).
 */
export interface LoginResponse {
  success: boolean;
  statusCode: number;
  message: string;
  token: string;
  user: User;
}

/**
 * Error response từ API
 */
export interface ErrorResponse {
  success: boolean;
  statusCode: number;
  message: string;
  error: string;
}