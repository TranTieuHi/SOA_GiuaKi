import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Alert, AlertDescription } from '../../../components/ui/alert';
import { AlertCircle } from 'lucide-react';
import { MainLayout } from '../../../components/layout/MainLayout';
import { StudentSearchForm } from '../components/StudentSearchForm';
import { StudentInfoCard } from '../components/StudentInfoCard';
import { PaymentConfirmCard } from '../components/PaymentConfirmCard';
import { searchStudent } from '../../../services/tuitionService';
import { getCurrentUser } from '../../authentication/services/authService';
import { Student } from '../../../types/tuition';

export function SearchStudentPage() {
  const navigate = useNavigate();
  const currentUser = getCurrentUser();

  const [student, setStudent] = useState<Student | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [searchError, setSearchError] = useState('');
  const [agreedToTerms, setAgreedToTerms] = useState(false);

  const userBalance = currentUser?.available_balance || 0;

  const handleSearch = async (studentId: string) => {
    setIsSearching(true);
    setSearchError('');
    setStudent(null);
    setAgreedToTerms(false);

    try {
      const result = await searchStudent(studentId);
      setStudent(result);
    } catch (error: any) {
      setSearchError(error.message);
    } finally {
      setIsSearching(false);
    }
  };

  const handleContinueToOTP = () => {
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

    if (userBalance < student.tuition_amount) {
      setSearchError('Số dư không đủ để thanh toán');
      return;
    }

    // Lưu thông tin sinh viên vào sessionStorage
    sessionStorage.setItem('payment_student', JSON.stringify(student));

    // Chuyển sang trang OTP
    navigate('/tuition/otp-verify');
  };

  return (
    <MainLayout>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold">Thanh toán học phí</h1>
          <p className="text-muted-foreground">Bước 1: Tìm kiếm sinh viên</p>
        </div>

        {/* Search Form */}
        <StudentSearchForm onSearch={handleSearch} isSearching={isSearching} />

        {/* Error Alert */}
        {searchError && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{searchError}</AlertDescription>
          </Alert>
        )}

        {/* Student Info */}
        {student && (
          <>
            <StudentInfoCard student={student} />

            {/* Payment Confirmation */}
            {!student.is_payed && (
              <PaymentConfirmCard
                student={student}
                userBalance={userBalance}
                agreedToTerms={agreedToTerms}
                onTermsChange={setAgreedToTerms}
                onContinue={handleContinueToOTP}
              />
            )}
          </>
        )}
      </div>
    </MainLayout>
  );
}