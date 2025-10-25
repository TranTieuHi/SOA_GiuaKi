import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/card';
import { CheckCircle, AlertCircle } from 'lucide-react';
import { Student } from '../../../types/tuition';

interface StudentInfoCardProps {
  student: Student;
}

export function StudentInfoCard({ student }: StudentInfoCardProps) {
  return (
    <Card className={student.is_payed ? 'border-green-200 bg-green-50' : 'border-blue-200 bg-blue-50'}>
      <CardHeader>
        <CardTitle className="text-lg flex items-center">
          {student.is_payed ? (
            <>
              <CheckCircle className="mr-2 text-green-600" /> Đã tìm thấy sinh viên
            </>
          ) : (
            <>
              <AlertCircle className="mr-2 text-blue-600" /> Thông tin sinh viên
            </>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-muted-foreground">Mã số sinh viên</p>
            <p className="font-semibold">{student.student_id}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Họ và tên</p>
            <p className="font-semibold">{student.full_name}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Lớp</p>
            <p className="font-semibold">{student.class}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Khoa</p>
            <p className="font-semibold">{student.faculty}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Học kỳ</p>
            <p className="font-semibold">{student.semester}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Năm học</p>
            <p className="font-semibold">{student.year}</p>
          </div>
        </div>

        <div className="pt-4 border-t">
          <p className="text-sm text-muted-foreground mb-1">Học phí</p>
          <p className="text-2xl font-bold text-red-600">
            {new Intl.NumberFormat('vi-VN', {
              style: 'currency',
              currency: 'VND',
            }).format(student.tuition_amount)}
          </p>
        </div>

        <div className="pt-2">
          <p className="text-sm text-muted-foreground">Trạng thái thanh toán</p>
          {student.is_payed ? (
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold bg-green-100 text-green-800">
              ✅ Đã thanh toán
            </span>
          ) : (
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold bg-red-100 text-red-800">
              ❌ Chưa thanh toán
            </span>
          )}
        </div>
      </CardContent>
    </Card>
  );
}