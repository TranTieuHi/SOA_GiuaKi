// filepath: client-react/src/features/authentication/components/LoginForm.tsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../../components/ui/card';
import { Button } from '../../../components/ui/button';
import { Input } from '../../../components/ui/input';
import { Label } from '../../../components/ui/label';
import { Eye, EyeOff, GraduationCap, AlertCircle } from 'lucide-react';
import { login } from '../services/authService'; // ✅ Updated import path

export function LoginForm() {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      console.log('🔄 Attempting login...');
      
      const response = await login({ 
        username: formData.username, 
        password: formData.password 
      });
      
      console.log('✅ Login successful:', response);
      
      // Verify token saved
      const savedToken = localStorage.getItem('token');
      const savedUser = localStorage.getItem('user');
      
      console.log('💾 Token saved:', savedToken ? 'Yes' : 'No');
      console.log('💾 User saved:', savedUser ? 'Yes' : 'No');
      
      if (!savedToken) {
        console.error('❌ Token was not saved!');
        setError('Login failed: Token not saved');
        return;
      }
      
      // Navigate to dashboard
      console.log('✅ Navigating to dashboard...');
      navigate('/dashboard', { replace: true });
      
    } catch (err: any) {
      console.error('❌ Login failed:', err);
      setError(err.message || 'Invalid username or password');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md shadow-lg">
        <CardHeader className="text-center space-y-4">
          <div className="mx-auto w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center">
            <GraduationCap className="w-8 h-8 text-white" />
          </div>
          <div>
            <CardTitle className="text-2xl">SOA Tuition System</CardTitle>
            <CardDescription className="mt-2">Đăng nhập để thanh toán học phí và quản lý tài khoản</CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Error Alert */}
            {error && (
              <div className="flex items-start gap-2 p-4 mb-4 text-sm text-red-800 bg-red-50 border border-red-200 rounded-lg">
                <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />
                <div className="flex-1">
                  <p className="font-medium">Đăng nhập thất bại</p>
                  <p className="mt-1">{error}</p>
                </div>
              </div>
            )}

            {/* Username */}
            <div className="space-y-2">
              <Label htmlFor="username">Tên đăng nhập (Email)</Label>
              <Input
                id="username"
                type="text"
                placeholder="hau6042004@gmail.com"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                disabled={isLoading}
                required
                autoComplete="username"
              />
            </div>

            {/* Password */}
            <div className="space-y-2">
              <Label htmlFor="password">Mật khẩu</Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="••••••••"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  disabled={isLoading}
                  required
                  autoComplete="current-password"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                  onClick={(e) => {
                    e.preventDefault();
                    setShowPassword(!showPassword);
                  }}
                  disabled={isLoading}
                  tabIndex={-1}
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4 text-muted-foreground" />
                  ) : (
                    <Eye className="h-4 w-4 text-muted-foreground" />
                  )}
                </Button>
              </div>
            </div>

            {/* Submit Button */}
            <Button 
              type="submit" 
              className="w-full" 
              disabled={isLoading || !formData.username.trim() || !formData.password.trim()}
            >
              {isLoading ? (
                <>
                  <span className="mr-2">⏳</span>
                  Đang đăng nhập...
                </>
              ) : (
                'Đăng nhập'
              )}
            </Button>

            {/* Forgot Password */}
            <div className="text-center">
              <Button 
                type="button" 
                variant="link" 
                className="text-sm text-muted-foreground"
                onClick={(e) => {
                  e.preventDefault();
                  console.log('Quên mật khẩu clicked');
                }}
                disabled={isLoading}
              >
                Quên mật khẩu?
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}