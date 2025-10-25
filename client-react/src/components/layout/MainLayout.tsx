import { ReactNode } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button } from '../ui/button'; // ✅ Add this import
import { LogOut, User, Home, CreditCard, History } from 'lucide-react';
import { getCurrentUser, logout } from '../../features/authentication/authService';

interface MainLayoutProps {
  children: ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const currentUser = getCurrentUser();

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Navbar */}
      <nav className="bg-white shadow-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center space-x-4">
              <h1 
                className="text-2xl font-bold text-blue-600 cursor-pointer"
                onClick={() => navigate('/dashboard')}
              >
                🎓 SOA Tuition System
              </h1>
            </div>

            {/* Navigation Links */}
            <div className="hidden md:flex items-center space-x-4">
              <Button
                variant={isActive('/dashboard') ? 'default' : 'ghost'}
                onClick={() => navigate('/dashboard')}
              >
                <Home className="w-4 h-4 mr-2" />
                Trang chủ
              </Button>

              <Button
                variant={isActive('/tuition') ? 'default' : 'ghost'}
                onClick={() => navigate('/tuition')}
              >
                <CreditCard className="w-4 h-4 mr-2" />
                Thanh toán
              </Button>

              <Button
                variant={isActive('/payment-history') ? 'default' : 'ghost'}
                onClick={() => navigate('/payment-history')}
              >
                <History className="w-4 h-4 mr-2" />
                Lịch sử
              </Button>
            </div>

            {/* User Info */}
            <div className="flex items-center space-x-4">
              <div className="text-right hidden sm:block">
                <p className="text-sm font-semibold">
                  {currentUser?.full_name || currentUser?.username}
                </p>
                <p className="text-xs text-muted-foreground">
                  {currentUser?.email_address}
                </p>
              </div>
              <Button 
                variant="outline" 
                size="icon"
                title="Hồ sơ"
              >
                <User className="h-5 w-5" />
              </Button>
              <Button 
                variant="destructive" 
                size="icon" 
                onClick={handleLogout}
                title="Đăng xuất"
              >
                <LogOut className="h-5 w-5" />
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="py-8 px-4 sm:px-6 lg:px-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-16">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-muted-foreground">
            © 2025 SOA Tuition Payment System. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}