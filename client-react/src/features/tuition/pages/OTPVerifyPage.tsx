import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../../../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/card';
import { Input } from '../../../components/ui/input';
import { Label } from '../../../components/ui/label';
import { Alert, AlertDescription } from '../../../components/ui/alert';
import { Shield, Loader2, AlertCircle, ArrowLeft, CheckCircle, Clock } from 'lucide-react';
import { MainLayout } from '../../../components/layout/MainLayout';
import { StudentInfoCard } from '../components/StudentInfoCard';
import { getCurrentUser } from '../../../services/authService';
import { generateOTP, sendOTP, verifyOTP } from '../../../services/otpService';
import { payTuition } from '../../../services/tuitionService';
import { Student } from '../../../types/tuition';

export function OTPVerifyPage() {
  const navigate = useNavigate();
  const currentUser = getCurrentUser();

  const [student, setStudent] = useState<Student | null>(null);
  const [otp, setOtp] = useState('');
  const [generatedOTP, setGeneratedOTP] = useState('');
  const [otpSent, setOtpSent] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isVerifying, setIsVerifying] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [countdown, setCountdown] = useState(0);

  useEffect(() => {
    // Lấy thông tin sinh viên từ sessionStorage
    const storedStudent = sessionStorage.getItem('payment_student');
    if (!storedStudent) {
      navigate('/tuition');
      return;
    }
    setStudent(JSON.parse(storedStudent));
  }, [navigate]);

  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [countdown]);

  // ✅ Tự động tạo và gửi OTP
  const handleRequestOTP = async () => {
    if (!currentUser || !student) return;

    setIsProcessing(true);
    setError('');
    setSuccess('');
    setOtp('');

    try {
      // 1. Tạo OTP
      console.log('🔑 Đang tạo mã OTP...');
      const generateResponse = await generateOTP({
        user_id: currentUser.user_id,
        email: currentUser.email_address,
      });

      const newOTP = generateResponse.data.otp || '';
      setGeneratedOTP(newOTP);
      console.log('✅ OTP đã tạo:', newOTP);

      // 2. Tự động gửi email (không cần user click)
      console.log('📧 Đang gửi OTP qua email...');
      await sendOTP({
        user_id: currentUser.user_id,
        email: currentUser.email_address,
        otp: newOTP,
      });

      setOtpSent(true);
      setSuccess(`📧 Mã OTP đã được gửi đến ${currentUser.email_address}`);
      setCountdown(60); // 60 giây mới được gửi lại
      console.log('✅ Email đã gửi thành công');
    } catch (err: any) {
      console.error('❌ Lỗi:', err);
      setError(err.message);
      setOtpSent(false);
    } finally {
      setIsProcessing(false);
    }
  };

  // ✅ Verify và thanh toán
  const handleVerifyAndPay = async () => {
    if (!currentUser || !student) return;

    if (!otp || otp.length !== 6) {
      setError('Vui lòng nhập mã OTP 6 chữ số');
      return;
    }

    setIsVerifying(true);
    setError('');

    try {
      console.log('🔐 Đang xác thực OTP...');

      // 1. Verify OTP
      await verifyOTP({
        user_id: currentUser.user_id,
        email: currentUser.email_address,
        otp: otp,
      });

      console.log('✅ OTP hợp lệ, đang thanh toán...');

      // 2. Thanh toán học phí
      const paymentResult = await payTuition({ student_id: student.student_id });

      // 3. Cập nhật số dư
      currentUser.available_balance = paymentResult.remaining_balance;
      localStorage.setItem('user', JSON.stringify(currentUser));

      // 4. Lưu kết quả thanh toán
      sessionStorage.setItem('payment_result', JSON.stringify(paymentResult));

      console.log('✅ Thanh toán thành công!');

      // 5. Chuyển sang trang thành công
      navigate('/tuition/success');
    } catch (err: any) {
      console.error('❌ Lỗi xác thực/thanh toán:', err);
      setError(err.message);
    } finally {
      setIsVerifying(false);
    }
  };

  if (!student) {
    return null;
  }

  return (
    <MainLayout>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold">Xác thực thanh toán</h1>
          <p className="text-muted-foreground">Bước 2: Nhập mã OTP</p>
        </div>

        {/* Back Button */}
        <Button variant="outline" onClick={() => navigate('/tuition')}>
          <ArrowLeft className="w-4 h-4 mr-2" /> Quay lại
        </Button>

        {/* Student Info */}
        <StudentInfoCard student={student} />

        {/* OTP Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Shield className="mr-2 text-blue-600" /> Xác thực OTP
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* ✅ Nếu chưa gửi OTP → Hiện nút "Nhận mã OTP" */}
            {!otpSent && (
              <div className="text-center space-y-4">
                <div className="p-6 bg-blue-50 rounded-lg border border-blue-200">
                  <Shield className="w-12 h-12 mx-auto text-blue-600 mb-3" />
                  <p className="text-sm text-muted-foreground mb-4">
                    Để bảo mật giao dịch, chúng tôi sẽ gửi mã OTP (6 chữ số) đến email của bạn
                  </p>
                  <p className="text-sm font-semibold text-blue-800">
                    📧 {currentUser?.email_address}
                  </p>
                </div>

                <Button
                  className="w-full"
                  size="lg"
                  onClick={handleRequestOTP}
                  disabled={isProcessing}
                >
                  {isProcessing ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Đang gửi mã OTP...
                    </>
                  ) : (
                    <>
                      <Shield className="w-5 h-5 mr-2" />
                      Nhận mã OTP qua Email
                    </>
                  )}
                </Button>
              </div>
            )}

            {/* ✅ Nếu đã gửi OTP → Hiện form nhập OTP */}
            {otpSent && (
              <div className="space-y-4">
                {/* Success Message */}
                <Alert className="border-green-500 bg-green-50">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <AlertDescription className="text-green-800">
                    {success}
                  </AlertDescription>
                </Alert>

                {/* OTP Input */}
                <div className="space-y-2">
                  <Label htmlFor="otp" className="text-base">
                    Nhập mã OTP (6 chữ số)
                  </Label>
                  <Input
                    id="otp"
                    type="text"
                    placeholder="● ● ● ● ● ●"
                    value={otp}
                    onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                    maxLength={6}
                    className="text-center text-3xl tracking-[1em] font-bold"
                    autoFocus
                  />
                  <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
                    <Clock className="w-4 h-4" />
                    <span>Mã OTP có hiệu lực trong 5 phút</span>
                  </div>
                </div>

                {/* Resend Button */}
                <Button
                  variant="outline"
                  className="w-full"
                  onClick={handleRequestOTP}
                  disabled={isProcessing || countdown > 0}
                >
                  {isProcessing ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Đang gửi lại...
                    </>
                  ) : countdown > 0 ? (
                    <>
                      <Clock className="w-4 h-4 mr-2" />
                      Gửi lại sau {countdown}s
                    </>
                  ) : (
                    '🔄 Gửi lại mã OTP'
                  )}
                </Button>

                {/* Verify Button */}
                <Button
                  className="w-full"
                  size="lg"
                  onClick={handleVerifyAndPay}
                  disabled={isVerifying || !otp || otp.length !== 6}
                >
                  {isVerifying ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Đang xử lý thanh toán...
                    </>
                  ) : (
                    <>
                      <CheckCircle className="w-5 h-5 mr-2" />
                      Xác nhận và thanh toán
                    </>
                  )}
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Help Text */}
        <Card className="bg-blue-50 border-blue-200">
          <CardContent className="pt-6">
            <div className="space-y-2 text-sm">
              <p className="font-semibold text-blue-900">💡 Lưu ý:</p>
              <ul className="list-disc list-inside space-y-1 text-blue-800 ml-2">
                <li>Kiểm tra hộp thư đến hoặc thư spam</li>
                <li>Mã OTP có hiệu lực trong 5 phút</li>
                <li>Bạn có thể gửi lại mã sau 60 giây</li>
                <li>Mỗi mã OTP chỉ sử dụng được 1 lần</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}