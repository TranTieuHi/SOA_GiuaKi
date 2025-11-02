import http from 'k6/http';
import { check } from 'k6'; // Dòng này đúng
import { Counter } from 'k6/metrics'; // 1. Import "Bộ đếm"

// --- 2. TẠO BỘ ĐẾM ---
// Chúng ta sẽ tạo 2 bộ đếm để xem kết quả cuối cùng
const successCounter = new Counter('payment_success_count'); // Đếm số lần 200 OK
const failureCounter = new Counter('payment_failure_count'); // Đếm các lỗi khác (400, 409...)

export const options = {
  stages: [
    { duration: '5s', target: 2 },
    { duration: '10s', target: 2 },
    { duration: '5s', target: 0 },
  ],
};

export default function () {
  const url = 'http://localhost:8001/payments/pay';
  const payload = JSON.stringify({
    student_id: 'ST2025002',
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
      // Nhớ dán Bearer Token của bạn vào đây
      'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiVVNSMTczNzYxODAwMDAwMCIsInVzZXJuYW1lIjoiam9obmRvZSIsImVtYWlsIjoiam9obmRvZUBleGFtcGxlLmNvbSIsImV4cCI6MTc2MjE3MDQxNn0.EyLdtUl-Rg8SKzOOP8IgI8milaR4q5IAN55XlUgwK3k',
    },
  };

  const res = http.post(url, payload, params);

  // --- 3. KHÔNG DÙNG CONSOLE.LOG ---
  // Thay vì log, chúng ta dùng check và tăng bộ đếm
  
  const isSuccess = check(res, {
    'status is 200 (Success)': (r) => r.status === 200,
  });

  if (isSuccess) {
    successCounter.add(1); // Tăng bộ đếm thành công
  } else {
    failureCounter.add(1); // Tăng bộ đếm thất bại
  }

  // Chúng ta xóa console.log ở đây, nên terminal sẽ im lặng khi chạy
}