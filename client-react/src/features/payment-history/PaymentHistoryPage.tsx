import { useState, useEffect } from 'react';
import { MainLayout } from '../../components/layout/MainLayout';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Alert, AlertDescription } from '../../components/ui/alert';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../../components/ui/table';
import { History, AlertCircle, Loader2, TrendingUp, Wallet, Calendar } from 'lucide-react';
import { getPaymentHistory, getPaymentStatistics } from '../../services/paymentService';
import { PaymentHistoryItem, PaymentStatistics } from '../../types/payment';

export function PaymentHistoryPage() {
  const [payments, setPayments] = useState<PaymentHistoryItem[]>([]);
  const [statistics, setStatistics] = useState<PaymentStatistics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [total, setTotal] = useState(0);
  const [limit] = useState(50);
  const [offset, setOffset] = useState(0);

  useEffect(() => {
    loadData();
  }, [offset]);

  const loadData = async () => {
    setIsLoading(true);
    setError('');

    try {
      const [historyResponse, statsResponse] = await Promise.all([
        getPaymentHistory(limit, offset),
        getPaymentStatistics(),
      ]);

      setPayments(historyResponse.data);
      setTotal(historyResponse.total);
      setStatistics(statsResponse.data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePreviousPage = () => {
    if (offset > 0) {
      setOffset(Math.max(0, offset - limit));
    }
  };

  const handleNextPage = () => {
    if (offset + limit < total) {
      setOffset(offset + limit);
    }
  };

  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold flex items-center justify-center gap-2">
            <History className="w-8 h-8" /> Lịch sử thanh toán
          </h1>
          <p className="text-muted-foreground mt-2">
            Xem lại các giao dịch thanh toán học phí đã thực hiện
          </p>
        </div>

        {/* Statistics Cards */}
        {statistics && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Tổng giao dịch</p>
                    <p className="text-2xl font-bold">{statistics.total_payments}</p>
                  </div>
                  <TrendingUp className="w-8 h-8 text-blue-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Tổng đã chi</p>
                    <p className="text-2xl font-bold text-red-600">
                      {new Intl.NumberFormat('vi-VN', {
                        style: 'currency',
                        currency: 'VND',
                      }).format(statistics.total_amount)}
                    </p>
                  </div>
                  <Wallet className="w-8 h-8 text-purple-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Giao dịch gần nhất</p>
                    <p className="text-lg font-semibold">
                      {statistics.last_payment
                        ? new Date(statistics.last_payment).toLocaleDateString('vi-VN')
                        : 'Chưa có'}
                    </p>
                  </div>
                  <Calendar className="w-8 h-8 text-green-500" />
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Payment History Table */}
        <Card>
          <CardHeader>
            <CardTitle>Danh sách giao dịch</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex justify-center items-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
                <span className="ml-2">Đang tải dữ liệu...</span>
              </div>
            ) : payments.length === 0 ? (
              <div className="text-center py-12">
                <History className="w-16 h-16 mx-auto text-muted-foreground mb-4" />
                <p className="text-muted-foreground">Chưa có giao dịch nào</p>
              </div>
            ) : (
              <>
                <div className="rounded-md border">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Mã GD</TableHead>
                        <TableHead>Ngày thanh toán</TableHead>
                        <TableHead>MSSV</TableHead>
                        <TableHead>Tên sinh viên</TableHead>
                        <TableHead>Lớp</TableHead>
                        <TableHead>Khoa</TableHead>
                        <TableHead className="text-right">Số tiền</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {payments.map((payment) => (
                        <TableRow key={payment.payment_id}>
                          <TableCell className="font-mono">
                            #{payment.payment_id}
                          </TableCell>
                          <TableCell>
                            {new Date(payment.payment_date).toLocaleString('vi-VN', {
                              year: 'numeric',
                              month: '2-digit',
                              day: '2-digit',
                              hour: '2-digit',
                              minute: '2-digit',
                            })}
                          </TableCell>
                          <TableCell className="font-semibold">
                            {payment.student_id}
                          </TableCell>
                          <TableCell>{payment.student_name}</TableCell>
                          <TableCell>{payment.class}</TableCell>
                          <TableCell>{payment.faculty}</TableCell>
                          <TableCell className="text-right font-bold text-green-600">
                            {new Intl.NumberFormat('vi-VN', {
                              style: 'currency',
                              currency: 'VND',
                            }).format(payment.amount || 0)} {/* Đổi thành payment.amount */}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>

                {/* Pagination */}
                <div className="flex items-center justify-between mt-4">
                  <div className="text-sm text-muted-foreground">
                    Hiển thị {offset + 1} - {Math.min(offset + limit, total)} / {total} giao dịch
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      onClick={handlePreviousPage}
                      disabled={offset === 0}
                    >
                      Trang trước
                    </Button>
                    <Button
                      variant="outline"
                      onClick={handleNextPage}
                      disabled={offset + limit >= total}
                    >
                      Trang sau
                    </Button>
                  </div>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}