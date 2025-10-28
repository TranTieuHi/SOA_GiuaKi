import { MainLayout } from '../../../components/layout/MainLayout';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { useNavigate } from 'react-router-dom';
import { CreditCard, History, Wallet, TrendingUp } from 'lucide-react';
import { getCurrentUser } from '../../authentication/services/authService';
import { useState, useEffect } from 'react';
import { getPaymentStatistics } from '../../../services/paymentService';
import { PaymentStatistics } from '../../../types/payment';

export function Dashboard() {
  const navigate = useNavigate();
  const currentUser = getCurrentUser();
  const [statistics, setStatistics] = useState<PaymentStatistics | null>(null);

  useEffect(() => {
    loadStatistics();
  }, []);

  const loadStatistics = async () => {
    try {
      const response = await getPaymentStatistics();
      setStatistics(response.data);
    } catch (error) {
      console.error('Failed to load statistics:', error);
    }
  };

  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Welcome Section */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold">
            Chào mừng, {currentUser?.full_name || currentUser?.username}! 👋
          </h1>
          <p className="text-muted-foreground text-lg">
            Hệ thống thanh toán học phí trực tuyến
          </p>
        </div>

        {/* Balance Card */}
        <Card className="bg-gradient-to-br from-blue-500 to-purple-600 text-white">
          <CardHeader>
            <CardTitle className="flex items-center text-white">
              <Wallet className="mr-2" /> Số dư tài khoản
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold">
              {new Intl.NumberFormat('vi-VN', {
                style: 'currency',
                currency: 'VND',
              }).format(currentUser?.available_balance || 0)}
            </div>
            <p className="text-blue-100 mt-2">Số dư khả dụng</p>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => navigate('/tuition')}>
            <CardHeader>
              <CardTitle className="flex items-center">
                <CreditCard className="mr-2 text-blue-600" /> Thanh toán học phí
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                Thanh toán học phí cho sinh viên nhanh chóng và an toàn
              </p>
              <Button className="mt-4 w-full">Thanh toán ngay</Button>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => navigate('/payment-history')}>
            <CardHeader>
              <CardTitle className="flex items-center">
                <History className="mr-2 text-green-600" /> Lịch sử giao dịch
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                Xem lại các giao dịch thanh toán đã thực hiện
              </p>
              <Button variant="outline" className="mt-4 w-full">Xem lịch sử</Button>
            </CardContent>
          </Card>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Tổng giao dịch</p>
                  <p className="text-2xl font-bold">{statistics?.total_payments || 0}</p>
                </div>
                <TrendingUp className="w-8 h-8 text-blue-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Thành công</p>
                  <p className="text-2xl font-bold text-green-600">{statistics?.total_payments || 0}</p>
                </div>
                <TrendingUp className="w-8 h-8 text-green-500" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Tổng đã chi</p>
                  <p className="text-2xl font-bold">
                    {new Intl.NumberFormat('vi-VN', {
                      style: 'currency',
                      currency: 'VND',
                    }).format(statistics?.total_amount || 0)}
                  </p>
                </div>
                <Wallet className="w-8 h-8 text-purple-500" />
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
}