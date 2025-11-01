import { Button } from "../ui/button";
import { Home, CreditCard, History, Settings, LogOut, Wallet } from "lucide-react";
import { useNavigate, useLocation } from "react-router-dom";
import { logout, getCurrentUser, refreshUserData } from "../../services/authService"; // ✅ Fixed import
import { useState, useEffect } from "react";

export function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const [user, setUser] = useState(getCurrentUser());
  const [isRefreshing, setIsRefreshing] = useState(false);

  // ✅ Refresh user data when component mounts or route changes
  useEffect(() => {
    const refreshData = async () => {
      try {
        setIsRefreshing(true);
        const freshUser = await refreshUserData();
        setUser(freshUser);
      } catch (error) {
        console.error('Failed to refresh user data:', error);
        // Keep current user data if refresh fails
        setUser(getCurrentUser());
      } finally {
        setIsRefreshing(false);
      }
    };

    // Refresh on mount and when returning from payment
    if (location.pathname === '/dashboard' || location.pathname === '/') {
      refreshData();
    } else {
      // Just update from localStorage for other routes
      setUser(getCurrentUser());
    }
  }, [location.pathname]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleRefreshBalance = async () => {
    try {
      setIsRefreshing(true);
      const freshUser = await refreshUserData();
      setUser(freshUser);
    } catch (error) {
      console.error('Failed to refresh balance:', error);
    } finally {
      setIsRefreshing(false);
    }
  };

  const menuItems = [
    { icon: Home, label: "Dashboard", path: "/dashboard" },
    { icon: CreditCard, label: "Thanh toán", path: "/tuition" },
    { icon: History, label: "Lịch sử", path: "/payment-history" },
    { icon: Settings, label: "Cài đặt", path: "/settings" },
  ];

  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-8">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                <span className="text-white font-bold">UB</span>
              </div>
              <span className="font-bold text-xl">University Banking</span>
            </div>
            
            <div className="hidden md:flex space-x-4">
              {menuItems.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                return (
                  <Button
                    key={item.path}
                    variant={isActive ? "default" : "ghost"}
                    onClick={() => navigate(item.path)}
                    className="flex items-center space-x-2"
                  >
                    <Icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </Button>
                );
              })}
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {/* ✅ Balance Display */}
            <div className="hidden md:block">
              <Button
                variant="outline"
                size="sm"
                onClick={handleRefreshBalance}
                disabled={isRefreshing}
                className="flex items-center space-x-2"
              >
                <Wallet className="w-4 h-4" />
                <span>
                  {isRefreshing ? (
                    <span className="animate-pulse">Đang tải...</span>
                  ) : (
                    <span className="font-semibold text-green-600">
                      {user?.available_balance ? 
                        new Intl.NumberFormat('vi-VN', {
                          style: 'currency',
                          currency: 'VND',
                        }).format(user.available_balance)
                        : '0 ₫'
                      }
                    </span>
                  )}
                </span>
              </Button>
            </div>

            {/* User Info */}
            <div className="text-right hidden md:block">
              <p className="text-sm font-medium">{user?.full_name || user?.username}</p>
              <p className="text-xs text-muted-foreground">{user?.email_address}</p>
            </div>

            <Button variant="outline" onClick={handleLogout}>
              <LogOut className="w-4 h-4 mr-2" />
              Đăng xuất
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
}