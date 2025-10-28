import { useState } from 'react';
import { Button } from '../../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Separator } from '../../components/ui/separator';
import { Checkbox } from '../../components/ui/checkbox';
import { Alert, AlertDescription } from '../../components/ui/alert';
import { Search, GraduationCap, CreditCard, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { searchStudent, payTuition } from '../../services/tuitionService';
import { getCurrentUser } from '../authentication/services/authService';
import { Student, PaymentResponse } from '../../types/tuition';
import { MainLayout } from '../../components/layout/MainLayout';

// ---- Component cho Bước 1: Nhập thông tin ----
function TuitionFormStep({
  studentId,
  setStudentId,
  student,
  isSearching,
  searchError,
  onSearch,
  agreedToTerms,
  setAgreedToTerms,
}: {
  studentId: string;
  setStudentId: (id: string) => void;
  student: Student | null;
  isSearching: boolean;
  searchError: string;
  onSearch: () => void;
  agreedToTerms: boolean;
  setAgreedToTerms: (agreed: boolean) => void;
}) {
  const currentUser = getCurrentUser();
  const userBalance = currentUser?.available_balance || 0;

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <GraduationCap className="mr-2" /> Thông tin sinh viên
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Label htmlFor="studentId">Mã số sinh viên (MSSV) *</Label>
          <div className="flex space-x-2">
            <Input
              id="studentId"
              placeholder="e.g., ST2025001"
              value={studentId}
              onChange={(e) => setStudentId(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && onSearch()}
              disabled={isSearching}
            />
            <Button
              variant="outline"
              onClick={onSearch}
              disabled={isSearching || !studentId.trim()}
            >
              {isSearching ? (
                <>
                  <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                  Đang tìm...
                </>
              ) : (
                <>
                  <Search className="w-4 h-4 mr-1" /> Tìm kiếm
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Error Alert */}
      {searchError && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{searchError}</AlertDescription>
        </Alert>
      )}

      {/* Student Found */}
      {student && (
        <>
          <Card className="border-green-200 bg-green-50">
            <CardHeader>
              <CardTitle className="text-lg text-green-800 flex items-center">
                <CheckCircle className="mr-2" /> Đã tìm thấy sinh viên
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <p>
                <strong>Họ tên:</strong> {student.full_name}
              </p>
              <p>
                <strong>Lớp:</strong> {student.class}
              </p>
              <p>
                <strong>Khoa:</strong> {student.faculty}
              </p>
              <p>
                <strong>Học kỳ:</strong> {student.semester}
              </p>
              <p>
                <strong>Năm học:</strong> {student.year}
              </p>
              <p>
                <strong>Học phí:</strong>{' '}
                {new Intl.NumberFormat('vi-VN', {
                  style: 'currency',
                  currency: 'VND',
                }).format(student.tuition_amount)}
              </p>
              <p>
                <strong>Trạng thái:</strong>{' '}
                {student.is_payed ? (
                  <span className="text-green-600 font-semibold">Đã thanh toán</span>
                ) : (
                  <span className="text-red-600 font-semibold">Chưa thanh toán</span>
                )}
              </p>
            </CardContent>
          </Card>

          {!student.is_payed && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <CreditCard className="mr-2" /> Chi tiết thanh toán
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>Số dư khả dụng</Label>
                  <div
                    className={`text-2xl font-bold ${
                      userBalance >= student.tuition_amount
                        ? 'text-green-600'
                        : 'text-red-600'
                    }`}
                  >
                    {new Intl.NumberFormat('vi-VN', {
                      style: 'currency',
                      currency: 'VND',
                    }).format(userBalance)}
                  </div>
                  {userBalance < student.tuition_amount && (
                    <p className="text-sm text-red-600 mt-2">
                      ⚠️ Số dư không đủ để thanh toán học phí
                    </p>
                  )}
                </div>
                <Separator />
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="terms"
                    checked={agreedToTerms}
                    onCheckedChange={(checked) => setAgreedToTerms(checked === true)}
                  />
                  <Label htmlFor="terms">
                    Tôi đồng ý với các điều khoản và điều kiện
                  </Label>
                </div>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  );
}

// ---- Component cho Bước 2: Xác nhận ----
function ConfirmStep({
  student,
  isProcessing,
  onConfirm,
}: {
  student: Student;
  isProcessing: boolean;
  onConfirm: () => void;
}) {
  const currentUser = getCurrentUser();

  return (
    <Card>
      <CardHeader>
        <CardTitle>Xác nhận thanh toán</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="p-4 border rounded-lg space-y-2">
          <h3 className="font-semibold">Thông tin người thanh toán</h3>
          <p>{currentUser?.full_name || currentUser?.username}</p>
          <p>{currentUser?.email_address}</p>
        </div>
        <div className="p-4 border rounded-lg space-y-2">
          <h3 className="font-semibold">Thông tin sinh viên</h3>
          <p>
            {student.full_name} ({student.student_id})
          </p>
          <p>Lớp: {student.class}</p>
          <p>Khoa: {student.faculty}</p>
          <p>Học kỳ: {student.semester} - Năm: {student.year}</p>
        </div>
        <div className="p-4 border rounded-lg space-y-2">
          <h3 className="font-semibold">Chi tiết giao dịch</h3>
          <div className="flex justify-between">
            <span>Số tiền</span>
            <strong>
              {new Intl.NumberFormat('vi-VN', {
                style: 'currency',
                currency: 'VND',
              }).format(student.tuition_amount)}
            </strong>
          </div>
          <div className="flex justify-between">
            <span>Phí giao dịch</span>
            <strong>0 VNĐ</strong>
          </div>
          <Separator />
          <div className="flex justify-between text-xl">
            <span>Tổng cộng</span>
            <strong className="text-blue-600">
              {new Intl.NumberFormat('vi-VN', {
                style: 'currency',
                currency: 'VND',
              }).format(student.tuition_amount)}
            </strong>
          </div>
        </div>

        <Button
          className="w-full"
          size="lg"
          onClick={onConfirm}
          disabled={isProcessing}
        >
          {isProcessing ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Đang xử lý...
            </>
          ) : (
            'Xác nhận thanh toán'
          )}
        </Button>
      </CardContent>
    </Card>
  );
}

// ---- Component cho Bước 3: Kết quả ----
function ResultStep({ paymentResult }: { paymentResult: PaymentResponse }) {
  return (
    <Card className="border-green-200 bg-green-50">
      <CardHeader>
        <CardTitle className="text-green-800 flex items-center justify-center text-2xl">
          <CheckCircle className="mr-2 w-8 h-8" /> Thanh toán thành công!
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="text-center space-y-2">
          <p className="text-lg">
            Bạn đã thanh toán thành công học phí cho sinh viên
          </p>
          <p className="text-2xl font-bold text-green-800">
            {paymentResult.student_name}
          </p>
        </div>

        <Separator />

        <div className="space-y-2">
          <div className="flex justify-between">
            <span>Mã giao dịch:</span>
            <strong>#{paymentResult.payment_id}</strong>
          </div>
          <div className="flex justify-between">
            <span>Mã sinh viên:</span>
            <strong>{paymentResult.student_id}</strong>
          </div>
          <div className="flex justify-between">
            <span>Số tiền đã thanh toán:</span>
            <strong className="text-green-600">
              {new Intl.NumberFormat('vi-VN', {
                style: 'currency',
                currency: 'VND',
              }).format(paymentResult.amount_paid)}
            </strong>
          </div>
          <div className="flex justify-between">
            <span>Thời gian:</span>
            <strong>
              {new Date(paymentResult.payment_date).toLocaleString('vi-VN')}
            </strong>
          </div>
          <div className="flex justify-between">
            <span>Số dư còn lại:</span>
            <strong className="text-blue-600">
              {new Intl.NumberFormat('vi-VN', {
                style: 'currency',
                currency: 'VND',
              }).format(paymentResult.remaining_balance)}
            </strong>
          </div>
        </div>

        <Button
          className="w-full mt-6"
          onClick={() => window.location.reload()}
        >
          Thanh toán cho sinh viên khác
        </Button>
      </CardContent>
    </Card>
  );
}

// ---- Component chính quản lý các bước ----
export function TuitionPage() {
  const [step, setStep] = useState(1);
  const [studentId, setStudentId] = useState('');
  const [student, setStudent] = useState<Student | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [searchError, setSearchError] = useState('');
  const [agreedToTerms, setAgreedToTerms] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [paymentResult, setPaymentResult] = useState<PaymentResponse | null>(null);

  const currentUser = getCurrentUser();

  const handleSearch = async () => {
    if (!studentId.trim()) {
      setSearchError('Vui lòng nhập mã sinh viên');
      return;
    }

    setIsSearching(true);
    setSearchError('');
    setStudent(null);

    try {
      const result = await searchStudent(studentId.trim());
      setStudent(result);
    } catch (error: any) {
      setSearchError(error.message);
    } finally {
      setIsSearching(false);
    }
  };

  const handleContinue = () => {
    if (!student) {
      setSearchError('Vui lòng tìm kiếm sinh viên trước');
      return;
    }

    if (student.is_payed) {
      setSearchError('Sinh viên này đã thanh toán học phí');
      return;
    }

    if (!agreedToTerms) {
      setSearchError('Vui lòng đồng ý với các điều khoản');
      return;
    }

    if (currentUser && currentUser.available_balance < student.tuition_amount) {
      setSearchError('Số dư không đủ để thanh toán');
      return;
    }

    setStep(2);
  };

  const handleConfirmPayment = async () => {
    if (!student) return;

    setIsProcessing(true);

    try {
      const result = await payTuition({ student_id: student.student_id });
      setPaymentResult(result);
      
      // Cập nhật số dư user trong localStorage
      if (currentUser) {
        currentUser.available_balance = result.remaining_balance;
        localStorage.setItem('user', JSON.stringify(currentUser));
      }
      
      setStep(3);
    } catch (error: any) {
      alert(`Thanh toán thất bại: ${error.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <MainLayout>
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="text-center">
          <h1 className="text-3xl font-bold">Thanh toán học phí</h1>
          <p className="text-muted-foreground">
            {step === 3 ? 'Hoàn thành' : `Bước ${step} / 2`}
          </p>
        </div>

        {step === 1 && (
          <TuitionFormStep
            studentId={studentId}
            setStudentId={setStudentId}
            student={student}
            isSearching={isSearching}
            searchError={searchError}
            onSearch={handleSearch}
            agreedToTerms={agreedToTerms}
            setAgreedToTerms={setAgreedToTerms}
          />
        )}

        {step === 2 && student && (
          <ConfirmStep
            student={student}
            isProcessing={isProcessing}
            onConfirm={handleConfirmPayment}
          />
        )}

        {step === 3 && paymentResult && <ResultStep paymentResult={paymentResult} />}

        {step < 3 && (
          <div className="flex justify-between">
            <Button
              variant="outline"
              onClick={() => setStep(Math.max(1, step - 1))}
              disabled={step === 1 || isProcessing}
            >
              Quay lại
            </Button>
            {step === 1 && (
              <Button
                onClick={handleContinue}
                disabled={
                  !student ||
                  student.is_payed ||
                  !agreedToTerms ||
                  isSearching
                }
              >
                Tiếp tục
              </Button>
            )}
          </div>
        )}
      </div>
    </MainLayout>
  );
}

// Export all tuition pages
export { SearchStudentPage } from './pages/SearchStudentPage';
export { OTPVerifyPage } from './pages/OTPVerifyPage';
export { PaymentSuccessPage } from './pages/PaymentSuccessPage';

// Export components
export { StudentInfoCard } from './components/StudentInfoCard';
export { StudentSearchForm } from './components/StudentSearchForm';
export { PaymentConfirmCard } from './components/PaymentConfirmCard';