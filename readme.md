 # GIưaKi — SOA Project

 Đây là README cho project "GIưaKi" (SOA_GiuaKi). Dự án gồm 3 thành phần chính:

 - `service-auth-fastapi`: microservice xác thực (FastAPI)
 - `service-tution-python`: microservice quản lý học phí / học sinh (FastAPI)
 - `client-react`: giao diện Frontend (React + Vite)

 Mục đích của tài liệu này: hướng dẫn setup, chạy project trên máy Windows (cmd.exe), mô tả các biến môi trường quan trọng, bảng dữ liệu chính và những vấn đề thường gặp cùng cách khắc phục.

 ## Mục lục
 - Yêu cầu
 - Cấu trúc project
 - Thiết lập môi trường (Windows)
 - Chạy từng service
 - Biến môi trường (.env) cần cấu hình
 - Cơ sở dữ liệu (bảng chính và kiểu dữ liệu)
 - Các API chính (tóm tắt)
 - Vấn đề thường gặp & cách khắc phục
 - Ghi chú dành cho developer

 ## Yêu cầu
 - Python 3.11+ (hoặc môi trường conda phù hợp)
 - Node.js 16+ (npm/yarn)
 - MySQL / MariaDB chạy cục bộ
 - pip packages: fastapi, uvicorn, pymysql, python-dotenv, passlib, bcrypt, python-jose
 - pnpm/npm for React (Vite)

 ## Cấu trúc project (tổng quan)

 ```
 GIuaKi/
 ├─ service-auth-fastapi/      # Auth service (FastAPI)
 ├─ service-tution-python/     # Tuition service (FastAPI)
 ├─ client-react/              # Frontend (React + Vite)
 └─ readme.md
 ```

 ## Thiết lập & chạy (Windows, cmd.exe)

 1) Thiết lập database

 - Tạo database (ví dụ `midterm_soa`) và import dữ liệu/schemas cần thiết.

 2) Auth service

 ```cmd
 cd service-auth-fastapi
 python -m venv venv
 venv\Scripts\activate
 pip install -r requirements.txt
 REM hoặc cài thủ công: pip install fastapi uvicorn pymysql python-dotenv passlib[bcrypt] python-jose
 uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
 ```

 3) Tuition service

 ```cmd
 cd service-tution-python
 python -m venv venv
 venv\Scripts\activate
 pip install -r requirements.txt
 uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
 ```

 4) Frontend (React + Vite)

 ```cmd
 cd client-react
 npm install
 npm run dev
 ```

 ## Các biến môi trường quan trọng

 Cả hai service FastAPI dùng file `.env`. Các giá trị quan trọng:

 - `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` — phải trỏ cùng database (`midterm_soa` trong repo này)
 - `JWT_SECRET_KEY` — phải giống giữa Auth service và Tuition service
 - (Tuition) `PORT=8001`, (Auth) `PORT=8000`

 Ví dụ `service-auth-fastapi/.env` và `service-tution-python/.env`:

 ```env
 DB_HOST=localhost
 DB_PORT=3306
 DB_USER=root
 DB_PASSWORD=
 DB_NAME=midterm_soa

 JWT_SECRET_KEY=change-this-to-same-value-in-both-services
 JWT_ALGORITHM=HS256
 ```

 ## Cấu trúc bảng `users` (quan trọng)

 Bảng `users` dùng chung giữa 2 service có cấu trúc chính (tối thiểu):

 - `user_id` varchar(36) PRIMARY KEY
 - `phone_number` varchar(20)
 - `email_address` varchar(100)
 - `password` varchar(100)        (bcrypt hash)
 - `username` varchar(50)
 - `full_name` varchar(100)
 - `available_balance` decimal(12,2)
 - `created_at` timestamp
 - `updated_at` timestamp

 Bảng `students` (tối thiểu):
 - `student_id` varchar(20) PK
 - `full_name` varchar(100)
 - `class` varchar(50)
 - `faculty` varchar(50)
 - `semester` varchar(20)
 - `year` int
 - `tuition_amount` decimal(12,2)
 - `is_payed` tinyint(1)
 - `created_at` timestamp
 - `version` int

 Bảng `payment_history` (ví dụ):
 - `id` int PK AUTO_INCREMENT
 - `user_id` varchar(36)
 - `student_id` varchar(20)
 - `created_at` timestamp

 ## Các API chính (tóm tắt)

 - Auth service (port 8000)
	 - POST `/api/auth/login` — đăng nhập
	 - POST `/api/auth/register` — đăng ký
	 - GET `/api/auth/profile` — profile hiện tại (yêu cầu token)

 - Tuition service (port 8001)
	 - GET `/students/search?student_id=ST...` — tìm sinh viên
	 - POST `/payments/pay` — thanh toán (yêu cầu token)
	 - GET `/payments/history` — lịch sử user

 - Frontend client (Vite) default port 5173

 ## Những vấn đề thường gặp & cách khắc phục

 1) Pydantic / environment conflicts
 - Nếu nhìn thấy lỗi khi import FastAPI / pydantic liên quan tới nhiều phiên bản pydantic, thường do packages cài ở user site và conda env cùng lúc. Giải pháp: dùng venv sạch hoặc đảm bảo `pip list` trong env chỉ có 1 pydantic.

 2) Bcrypt & passlib errors
 - Bcrypt giới hạn password 72 bytes — nếu dùng mật khẩu dài, truncate trước khi hash/verify.
 - Nếu passlib báo lỗi `module 'bcrypt' has no attribute '__about__'` thì hãy cài phiên bản tương thích: `pip install bcrypt==4.1.2 passlib[bcrypt]==1.7.4` hoặc dùng venv sạch.

 3) JWT signature verification failed
 - Đảm bảo `JWT_SECRET_KEY` giống hệt giữa Auth service và Tuition service.

 4) Route 404 do prefix sai
 - Chú ý baseURL ở frontend: nếu backend route là `/students/search`, thì `tuitionApi.baseURL` nên là `http://localhost:8001` (không kèm `/api`) — hoặc đồng bộ cả hai.

 5) Số dư không cập nhật ngay trên Dashboard
 - Nguyên nhân thường là cache connection / connection pool / isolation level. Giải pháp: dùng kết nối mới khi đọc `profile` hoặc gọi endpoint force-refresh (`/auth/profile/refresh`) sau khi thanh toán để đảm bảo đọc dữ liệu mới nhất; client nên cập nhật `localStorage` từ response mới và dashboard gọi API refresh khi navigation trở về.

 ## Debug & test nhanh

 - Test health endpoints:
 ```cmd
 curl http://localhost:8001/health
 curl http://localhost:8000/health
 ```

 - Test student search:
 ```cmd
 curl "http://localhost:8001/students/search?student_id=ST2025004"
 ```

 - Test login (Auth):
 ```cmd
 curl -X POST http://localhost:8000/api/auth/login -H "Content-Type: application/json" -d "{\"username\":\"johndoe\",\"password\":\"password123\"}"
 ```

 - Test payment (use token from login):
 ```cmd
 curl -X POST http://localhost:8001/payments/pay -H "Content-Type: application/json" -H "Authorization: Bearer <TOKEN>" -d "{\"student_id\":\"ST2025004\"}"
 ```

 ## Gợi ý developer / bước tiếp theo

 - Đồng bộ `JWT_SECRET_KEY` trong cả hai service
 - Dùng venv cho từng service thay vì dùng global/conda đễ tránh xung đột phiên bản
 - Thêm endpoint `POST /auth/profile/refresh` nếu cần đảm bảo fresh read ngay sau transaction
 - Cân nhắc đóng/mở connection pool hoặc set `autocommit`/isolation level để tránh đọc dữ liệu cũ

 ## Liên hệ
 - Nếu cần trợ giúp chi tiết hơn, gửi log terminal của 2 service khi thực hiện payment và profile read (kèm thời gian) — tôi sẽ phân tích giúp.

 ---
 _README tự động tạo vào ngày: 2025-11-03_
