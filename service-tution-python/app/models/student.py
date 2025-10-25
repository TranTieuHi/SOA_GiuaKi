from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class StudentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    student_id: str
    full_name: str
    class_name: str = Field(alias="class")  # Dùng alias vì 'class' là keyword
    faculty: Optional[str] = None
    semester: str = "Fall 2024"  # ✅ Thêm semester
    year: int = 2024  # ✅ Thêm year
    tuition_amount: float
    is_payed: bool = False

class StudentResponse(StudentBase):
    created_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "ST2025001",
                "full_name": "Nguyen Van A",
                "class": "CNTT-K18",
                "faculty": "Faculty of Information Technology",
                "semester": "Fall 2024",
                "year": 2024,
                "tuition_amount": 15000000.0,
                "is_payed": False,
                "created_at": "2025-10-23T10:00:00"
            }
        }

class StudentSearchRequest(BaseModel):
    student_id: Optional[str] = None
    full_name: Optional[str] = None
    semester: Optional[str] = None  # ✅ Thêm tìm kiếm theo semester
    year: Optional[int] = None  # ✅ Thêm tìm kiếm theo year
    
    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "ST2025001",
                "full_name": "Nguyen Van A",
                "semester": "Fall 2024",
                "year": 2024
            }
        }

class StudentListResponse(BaseModel):
    students: list[StudentResponse]
    total_count: int
    total_unpaid_amount: float
    unpaid_count: int

    class Config:
        json_schema_extra = {
            "example": {
                "students": [
                    {
                        "student_id": "ST2025001",
                        "full_name": "Nguyen Van A",
                        "class": "CNTT-K18",
                        "faculty": "Faculty of Information Technology",
                        "semester": "Fall 2024",
                        "year": 2024,
                        "tuition_amount": 15000000.0,
                        "is_payed": False,
                        "created_at": "2025-10-23T10:00:00"
                    }
                ],
                "total_count": 5,
                "total_unpaid_amount": 70500000.0,
                "unpaid_count": 4
            }
        }