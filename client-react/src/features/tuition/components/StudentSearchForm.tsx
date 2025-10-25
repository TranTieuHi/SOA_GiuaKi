import { useState } from 'react';
import { Button } from '../../../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/card';
import { Input } from '../../../components/ui/input';
import { Label } from '../../../components/ui/label';
import { Search, GraduationCap, Loader2 } from 'lucide-react';

interface StudentSearchFormProps {
  onSearch: (studentId: string) => void;
  isSearching: boolean;
}

export function StudentSearchForm({ onSearch, isSearching }: StudentSearchFormProps) {
  const [studentId, setStudentId] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (studentId.trim()) {
      onSearch(studentId.trim());
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <GraduationCap className="mr-2" /> Tìm kiếm sinh viên
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <Label htmlFor="studentId">Mã số sinh viên (MSSV) *</Label>
              <div className="flex space-x-2 mt-2">
                <Input
                  id="studentId"
                  placeholder="Nhập MSSV (vd: ST2025001)"
                  value={studentId}
                  onChange={(e) => setStudentId(e.target.value)}
                  disabled={isSearching}
                  className="flex-1"
                />
                <Button
                  type="submit"
                  variant="outline"
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
            </div>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}