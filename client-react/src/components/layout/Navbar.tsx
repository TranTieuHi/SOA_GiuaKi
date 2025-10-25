import { Button } from "../ui/button";
import { Home, CreditCard, History, Settings, LogOut } from "lucide-react";
import { useNavigate, useLocation } from "react-router-dom";
import { logout, getCurrentUser } from "../../features/authentication/authService";

export function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const user = getCurrentUser();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const menuItems = [
    { icon: Home, label: "Dashboard", path: "/dashboard" },
    { icon: CreditCard, label: "Thanh toán", path: "/tuition" },
    { icon: History, label: "Lịch sử", path: "/history" },
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