import { MainLayout } from '../../../components/layout/MainLayout';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { useNavigate, useLocation } from 'react-router-dom';
import { CreditCard, History, Wallet, TrendingUp, RefreshCw } from 'lucide-react';
import { getCurrentUser, refreshUserData } from '../../../services/authService';
import { useState, useEffect } from 'react';
import { getPaymentStatistics } from '../../../services/paymentService';
import { PaymentStatistics } from '../../../types/payment';

export function Dashboard() {
  const navigate = useNavigate();
  const location = useLocation();
  const [currentUser, setCurrentUser] = useState(getCurrentUser());
  const [statistics, setStatistics] = useState<PaymentStatistics | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastUpdateTime, setLastUpdateTime] = useState(new Date());

  // ✅ Enhanced refresh logic
  useEffect(() => {
    const fromPayment = sessionStorage.getItem('just_completed_payment');
    const forceRefresh = location.state?.forceRefresh;
    
    console.log('🔄 Dashboard useEffect triggered');
    console.log('   - fromPayment:', fromPayment);
    console.log('   - forceRefresh:', forceRefresh);
    console.log('   - location.key:', location.key);
    
    if (fromPayment || forceRefresh) {
      console.log('🔄 Detected return from payment - forcing refresh...');
      sessionStorage.removeItem('just_completed_payment');
      
      // Force refresh with delay
      setTimeout(() => {
        loadDashboardData(true); // true = force refresh
      }, 500);
    } else {
      loadDashboardData();
    }
  }, [location.key, location.state]);

  // ✅ Auto-refresh every 30 seconds when user is on dashboard
  useEffect(() => {
    const interval = setInterval(() => {
      if (document.visibilityState === 'visible') {
        console.log('🔄 Auto-refreshing dashboard data...');
        loadDashboardData();
      }
    }, 30000); // 30 seconds

    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async (forceRefresh = false) => {
    try {
      setIsRefreshing(true);
      
      console.log('\n' + '='.repeat(60));
      console.log('🔄 LOADING DASHBOARD DATA');
      console.log('='.repeat(60));
      console.log('   Force refresh:', forceRefresh);
      
      // ✅ Always refresh user data from API
      console.log('🔄 Dashboard: Refreshing user data...');
      const freshUser = await refreshUserData();
      setCurrentUser(freshUser);
      setLastUpdateTime(new Date());
      
      console.log('💰 Dashboard balance updated:', freshUser.available_balance.toLocaleString('vi-VN'));
      
      // Load statistics (optional, can skip if slow)
      try {
        const response = await getPaymentStatistics();
        setStatistics(response.data);
      } catch (statsError) {
        console.warn('⚠️ Failed to load statistics:', statsError);
        // Don't fail the whole refresh for statistics
      }
      
      console.log('✅ Dashboard data loaded successfully');
      console.log('='.repeat(60) + '\n');
      
    } catch (error) {
      console.error('❌ Failed to load dashboard data:', error);
      // Fallback to localStorage data
      const fallbackUser = getCurrentUser();
      setCurrentUser(fallbackUser);
      console.log('📱 Using fallback localStorage data');
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleRefreshData = async () => {
    await loadDashboardData(true);
  };

  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Welcome Section */}
        <div className="text-center space-y-2">
          <div className="flex items-center justify-center space-x-4">
            <h1 className="text-4xl font-bold">
              Chào mừng, {currentUser?.full_name || currentUser?.username}! 👋
            </h1>
            {/* ✅ Add refresh button */}
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefreshData}
              disabled={isRefreshing}
              className="flex items-center space-x-1"
            >
              <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
              <span>{isRefreshing ? 'Đang tải...' : 'Làm mới'}</span>
            </Button>
          </div>
          <p className="text-muted-foreground text-lg">
            Hệ thống thanh toán học phí trực tuyến
          </p>
        </div>

        {/* Balance Card */}
        <Card className="bg-gradient-to-br from-blue-500 to-purple-600 text-white">
          <CardHeader>
            <CardTitle className="flex items-center justify-between text-white">
              <div className="flex items-center">
                <Wallet className="mr-2" /> Số dư tài khoản
              </div>
              {/* ✅ Show loading indicator */}
              {isRefreshing && (
                <RefreshCw className="w-5 h-5 animate-spin text-white/80" />
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold">
              {isRefreshing ? (
                <span className="animate-pulse">Đang cập nhật...</span>
              ) : (
                new Intl.NumberFormat('vi-VN', {
                  style: 'currency',
                  currency: 'VND',
                }).format(currentUser?.available_balance || 0)
              )}
            </div>
            <p className="text-blue-100 mt-2">
              Số dư khả dụng {!isRefreshing && '(Đã cập nhật)'}
            </p>
            
            {/* ✅ Show last update time */}
            <p className="text-blue-200 text-xs mt-1">
              Cập nhật lần cuối: {lastUpdateTime.toLocaleTimeString('vi-VN')}
            </p>
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
                  <p className="text-2xl font-bold">
                    {isRefreshing ? (
                      <span className="animate-pulse">--</span>
                    ) : (
                      statistics?.total_payments || 0
                    )}
                  </p>
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
                  <p className="text-2xl font-bold text-green-600">
                    {isRefreshing ? (
                      <span className="animate-pulse">--</span>
                    ) : (
                      statistics?.total_payments || 0
                    )}
                  </p>
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
                    {isRefreshing ? (
                      <span className="animate-pulse">--</span>
                    ) : (
                      new Intl.NumberFormat('vi-VN', {
                        style: 'currency',
                        currency: 'VND',
                      }).format(statistics?.total_amount || 0)
                    )}
                  </p>
                </div>
                <Wallet className="w-8 h-8 text-purple-500" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* ✅ Enhanced status info */}
        <Card className="bg-green-50 border-green-200">
          <CardContent className="pt-4">
            <div className="space-y-2">
              <div className="flex items-center space-x-2 text-green-800">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <p className="text-sm">
                  Dashboard tự động cập nhật số dư mới nhất khi bạn quay về sau khi thanh toán
                </p>
              </div>
              <div className="text-xs text-green-600">
                💰 Số dư hiện tại: <strong>{currentUser?.available_balance?.toLocaleString('vi-VN')} VND</strong>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}