import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../../../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/card';
import { Separator } from '../../../components/ui/separator';
import { CheckCircle, Home, Receipt, ArrowRight } from 'lucide-react';
import { MainLayout } from '../../../components/layout/MainLayout';
import { PaymentResponse } from '../../../types/tuition';
import Confetti from 'react-confetti';
import { useWindowSize } from '@uidotdev/usehooks';

export function PaymentSuccessPage() {
  const navigate = useNavigate();
  const { width, height } = useWindowSize();
  const [paymentResult, setPaymentResult] = useState<PaymentResponse | null>(null);
  const [showConfetti, setShowConfetti] = useState(true);

  useEffect(() => {
    // Lấy kết quả thanh toán từ sessionStorage
    const storedResult = sessionStorage.getItem('payment_result');
    if (!storedResult) {
      navigate('/tuition');
      return;
    }
    setPaymentResult(JSON.parse(storedResult));

    // Tắt confetti sau 5 giây
    const timer = setTimeout(() => setShowConfetti(false), 5000);
    return () => clearTimeout(timer);
  }, [navigate]);

  const handleNewPayment = () => {
    // Xóa dữ liệu cũ
    sessionStorage.removeItem('payment_student');
    sessionStorage.removeItem('payment_result');
    navigate('/tuition');
  };

  const handleGoHome = () => {
    // Xóa dữ liệu cũ
    sessionStorage.removeItem('payment_student');
    sessionStorage.removeItem('payment_result');
    navigate('/');
  };

  const handleViewHistory = () => {
    // Xóa dữ liệu cũ
    sessionStorage.removeItem('payment_student');
    sessionStorage.removeItem('payment_result');
    navigate('/payment-history');
  };

  if (!paymentResult) {
    return null;
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
            {/* Transaction Info */}
            <div className="space-y-3">
              <div className="flex justify-between py-2">
                <span className="text-muted-foreground">Mã giao dịch:</span>
                <strong className="text-blue-600">#{paymentResult.payment_id}</strong>
              </div>

              <div className="flex justify-between py-2">
                <span className="text-muted-foreground">Mã sinh viên:</span>
                <strong>{paymentResult.student_id}</strong>
              </div>

              <div className="flex justify-between py-2">
                <span className="text-muted-foreground">Người thanh toán:</span>
                <strong>{paymentResult.user_id}</strong>
              </div>

              <div className="flex justify-between py-2">
                <span className="text-muted-foreground">Thời gian:</span>
                <strong>
                  {new Date(paymentResult.payment_date).toLocaleString('vi-VN', {
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit',
                  })}
                </strong>
              </div>

              <Separator />

              <div className="flex justify-between py-2">
                <span className="text-muted-foreground">Số tiền đã thanh toán:</span>
                <strong className="text-2xl text-green-600">
                  {new Intl.NumberFormat('vi-VN', {
                    style: 'currency',
                    currency: 'VND',
                  }).format(paymentResult.amount_paid || 0)}
                </strong>
              </div>

              <div className="flex justify-between py-2">
                <span className="text-muted-foreground">Số dư còn lại:</span>
                <strong className="text-xl text-blue-600">
                  {new Intl.NumberFormat('vi-VN', {
                    style: 'currency',
                    currency: 'VND',
                  }).format(paymentResult.remaining_balance)}
                </strong>
              </div>
            </div>

            {/* Success Message */}
            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-center text-green-800">
                ✅ <strong>{paymentResult.message}</strong>
              </p>
              <p className="text-center text-sm text-muted-foreground mt-2">
                Biên lai thanh toán đã được gửi đến email của bạn
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
                <li>Vui lòng kiểm tra email để nhận biên lai điện tử</li>
                <li>Mã giao dịch có thể được sử dụng để tra cứu sau này</li>
                <li>Nếu có bất kỳ thắc mắc, vui lòng liên hệ bộ phận hỗ trợ</li>
                <li>Thông tin thanh toán đã được cập nhật vào hệ thống</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}