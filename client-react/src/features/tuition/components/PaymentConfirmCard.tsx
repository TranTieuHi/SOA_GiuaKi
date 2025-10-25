import { Button } from '../../../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/card';
import { Separator } from '../../../components/ui/separator';
import { Checkbox } from '../../../components/ui/checkbox';
import { Label } from '../../../components/ui/label';
import { CreditCard, AlertCircle } from 'lucide-react';
import { Student } from '../../../types/tuition';

interface PaymentConfirmCardProps {
  student: Student;
  userBalance: number;
  agreedToTerms: boolean;
  onTermsChange: (agreed: boolean) => void;
  onContinue: () => void;
}

export function PaymentConfirmCard({
  student,
  userBalance,
  agreedToTerms,
  onTermsChange,
  onContinue,
}: PaymentConfirmCardProps) {
  const canPay = userBalance >= student.tuition_amount;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <CreditCard className="mr-2" /> Xác nhận thanh toán
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* User Balance */}
        <div>
          <Label>Số dư khả dụng của bạn</Label>
          <div
            className={`text-2xl font-bold ${
              canPay ? 'text-green-600' : 'text-red-600'
            }`}
          >
            {new Intl.NumberFormat('vi-VN', {
              style: 'currency',
              currency: 'VND',
            }).format(userBalance)}
          </div>
          {!canPay && (
            <div className="flex items-center space-x-2 text-sm text-red-600 mt-2">
              <AlertCircle className="w-4 h-4" />
              <span>Số dư không đủ để thanh toán học phí</span>
            </div>
          )}
        </div>

        <Separator />

        {/* Payment Summary */}
        <div className="p-4 bg-gray-50 rounded-lg space-y-2">
          <div className="flex justify-between">
            <span>Học phí:</span>
            <strong>
              {new Intl.NumberFormat('vi-VN', {
                style: 'currency',
                currency: 'VND',
              }).format(student.tuition_amount)}
            </strong>
          </div>
          <div className="flex justify-between">
            <span>Phí giao dịch:</span>
            <strong>0 ₫</strong>
          </div>
          <Separator />
          <div className="flex justify-between text-xl">
            <span className="font-semibold">Tổng thanh toán:</span>
            <strong className="text-red-600">
              {new Intl.NumberFormat('vi-VN', {
                style: 'currency',
                currency: 'VND',
              }).format(student.tuition_amount)}
            </strong>
          </div>
        </div>

        {/* Terms Checkbox */}
        <div className="flex items-start space-x-2">
          <Checkbox
            id="terms"
            checked={agreedToTerms}
            onCheckedChange={(checked) => onTermsChange(checked === true)}
          />
          <Label htmlFor="terms" className="text-sm leading-relaxed">
            Tôi đồng ý với các điều khoản và xác nhận thông tin thanh toán là chính xác
          </Label>
        </div>

        {/* Continue Button */}
        <Button
          className="w-full"
          size="lg"
          onClick={onContinue}
          disabled={!agreedToTerms || !canPay}
        >
          Tiếp tục xác thực OTP
        </Button>
      </CardContent>
    </Card>
  );
}