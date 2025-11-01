import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../../../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/card';
import { Separator } from '../../../components/ui/separator';
import { CheckCircle, Home, Receipt, ArrowRight, User, GraduationCap } from 'lucide-react';
import { MainLayout } from '../../../components/layout/MainLayout';
import { PaymentResponse } from '../../../types/tuition';
import { getUserProfile, UserProfile, refreshUserData } from '../../../services/authService'; // ✅ Fixed import
import Confetti from 'react-confetti';
import { useWindowSize } from '@uidotdev/usehooks';

export function PaymentSuccessPage() {
  const navigate = useNavigate();
  const { width, height } = useWindowSize();
  const [paymentResult, setPaymentResult] = useState<PaymentResponse | null>(null);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [showConfetti, setShowConfetti] = useState(true);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadPaymentData = async () => {
      try {
        // Lấy kết quả thanh toán từ sessionStorage
        const storedResult = sessionStorage.getItem('payment_result');
        if (!storedResult) {
          navigate('/tuition');
          return;
        }

        const paymentData = JSON.parse(storedResult);
        setPaymentResult(paymentData);

        // ✅ Set flag for Dashboard to know user just completed payment
        sessionStorage.setItem('just_completed_payment', 'true');

        // ✅ Refresh user data in localStorage với số dư mới
        console.log('🔄 Refreshing user data after successful payment...');
        await refreshUserData();

        // Lấy thông tin user profile
        const profile = await getUserProfile();
        setUserProfile(profile);

        setLoading(false);

        // Tắt confetti sau 5 giây
        const timer = setTimeout(() => setShowConfetti(false), 5000);
        return () => clearTimeout(timer);
      } catch (error) {
        console.error('❌ Error loading payment data:', error);
        navigate('/tuition');
      }
    };

    loadPaymentData();
  }, [navigate]);

  const handleNewPayment = async () => {
    // ✅ Refresh user data trước khi chuyển trang
    try {
      await refreshUserData();
    } catch (error) {
      console.error('Failed to refresh user data:', error);
    }
    
    // Xóa dữ liệu cũ
    sessionStorage.removeItem('payment_student');
    sessionStorage.removeItem('payment_result');
    navigate('/tuition');
  };

  const handleGoHome = async () => {
    // ✅ Refresh user data trước khi về trang chủ
    try {
      await refreshUserData();
      sessionStorage.setItem('just_completed_payment', 'true'); // Set flag
    } catch (error) {
      console.error('Failed to refresh user data:', error);
    }
    
    // Xóa dữ liệu cũ
    sessionStorage.removeItem('payment_student');
    sessionStorage.removeItem('payment_result');
    
    // Navigate with state to force refresh
    navigate('/dashboard', { state: { forceRefresh: true } });
  };

  const handleViewHistory = async () => {
    // ✅ Refresh user data trước khi xem lịch sử
    try {
      await refreshUserData();
    } catch (error) {
      console.error('Failed to refresh user data:', error);
    }
    
    // Xóa dữ liệu cũ
    sessionStorage.removeItem('payment_student');
    sessionStorage.removeItem('payment_result');
    navigate('/payment-history');
  };

  if (loading || !paymentResult || !userProfile) {
    return (
      <MainLayout>
        <div className="max-w-4xl mx-auto">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <span className="ml-3">Đang tải thông tin thanh toán...</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      {showConfetti && width && height && (
        <Confetti
          width={width}
          height={height}
          recycle={false}
          numberOfPieces={500}
        />
      )}

      <div className="max-w-4xl mx-auto space-y-6">
        {/* Success Header */}
        <Card className="border-green-200 bg-gradient-to-br from-green-50 to-white">
          <CardHeader className="text-center">
            <div className="flex justify-center mb-4">
              <div className="bg-green-100 p-4 rounded-full">
                <CheckCircle className="w-16 h-16 text-green-600" />
              </div>
            </div>
            <CardTitle className="text-3xl text-green-800">
              🎉 Thanh toán thành công!
            </CardTitle>
            <p className="text-muted-foreground mt-2">
              Giao dịch của bạn đã được xử lý thành công
            </p>
          </CardHeader>
        </Card>

        {/* Payment Details */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Receipt className="mr-2" /> Chi tiết giao dịch
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Student Info */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold flex items-center text-blue-600">
                <GraduationCap className="w-5 h-5 mr-2" />
                Thông tin sinh viên
              </h3>
              
              <div className="flex justify-between py-2">
                <span className="text-muted-foreground">Mã sinh viên:</span>
                <strong className="text-blue-600">{paymentResult.data.student_id}</strong>
              </div>

              <div className="flex justify-between py-2">
                <span className="text-muted-foreground">Tên sinh viên:</span>
                <strong>{paymentResult.data.student_name}</strong>
              </div>

              <div className="flex justify-between py-2">
                <span className="text-muted-foreground">Lớp:</span>
                <strong>{paymentResult.data.student_class}</strong>
              </div>

              <div className="flex justify-between py-2">
                <span className="text-muted-foreground">Khoa:</span>
                <strong>{paymentResult.data.student_faculty}</strong>
              </div>

              <Separator />

              {/* User Info */}
              <h3 className="text-lg font-semibold flex items-center text-green-600">
                <User className="w-5 h-5 mr-2" />
                Người thanh toán
              </h3>

              <div className="flex justify-between py-2">
                <span className="text-muted-foreground">Họ và tên:</span>
                <strong>{userProfile.full_name}</strong>
              </div>

              <div className="flex justify-between py-2">
                <span className="text-muted-foreground">Tài khoản:</span>
                <strong>{userProfile.username}</strong>
              </div>

              <div className="flex justify-between py-2">
                <span className="text-muted-foreground">Email:</span>
                <strong>{userProfile.email_address}</strong>
              </div>

              <Separator />

              {/* Payment Info */}
              <h3 className="text-lg font-semibold text-purple-600">
                Thông tin thanh toán
              </h3>

              <div className="flex justify-between py-2">
                <span className="text-muted-foreground">Thời gian thanh toán:</span>
                <strong>
                  {new Date(paymentResult.data.payment_date).toLocaleString('vi-VN', {
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit',
                  })}
                </strong>
              </div>

              <div className="flex justify-between py-2">
                <span className="text-muted-foreground">Số tiền đã thanh toán:</span>
                <strong className="text-2xl text-green-600">
                  {new Intl.NumberFormat('vi-VN', {
                    style: 'currency',
                    currency: 'VND',
                  }).format(paymentResult.data.amount_paid)}
                </strong>
              </div>

              <div className="flex justify-between py-2">
                <span className="text-muted-foreground">Số dư tài khoản còn lại:</span>
                <strong className="text-xl text-blue-600">
                  {new Intl.NumberFormat('vi-VN', {
                    style: 'currency',
                    currency: 'VND',
                  }).format(paymentResult.data.remaining_balance)}
                </strong>
              </div>
            </div>

            {/* Success Message */}
            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-center text-green-800">
                ✅ <strong>{paymentResult.message}</strong>
              </p>
              <p className="text-center text-sm text-muted-foreground mt-2">
                Học phí đã được thanh toán thành công cho sinh viên <strong>{paymentResult.data.student_name}</strong>
              </p>
              <p className="text-center text-sm text-muted-foreground">
                Biên lai thanh toán đã được gửi đến email: <strong>{userProfile.email_address}</strong>
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <Card>
          <CardContent className="pt-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Button
                variant="outline"
                className="w-full"
                onClick={handleGoHome}
              >
                <Home className="w-4 h-4 mr-2" />
                Về trang chủ
              </Button>

              <Button
                variant="outline"
                className="w-full"
                onClick={handleViewHistory}
              >
                <Receipt className="w-4 h-4 mr-2" />
                Xem lịch sử
              </Button>

              <Button
                className="w-full"
                onClick={handleNewPayment}
              >
                Thanh toán tiếp
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Additional Info */}
        <Card className="bg-blue-50 border-blue-200">
          <CardContent className="pt-6">
            <div className="space-y-2 text-sm text-blue-800">
              <p>📌 <strong>Lưu ý quan trọng:</strong></p>
              <ul className="list-disc list-inside space-y-1 ml-4">
                <li>Vui lòng kiểm tra email <strong>{userProfile.email_address}</strong> để nhận biên lai điện tử</li>
                <li>Thông tin thanh toán đã được cập nhật vào hệ thống trường</li>
                <li>Sinh viên <strong>{paymentResult.data.student_name}</strong> đã hoàn thành việc đóng học phí</li>
                <li>Nếu có bất kỳ thắc mắc, vui lòng liên hệ bộ phận tài chính trường</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}