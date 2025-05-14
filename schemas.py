# schemas.py

from pydantic import BaseModel, Field, EmailStr
from datetime import date
from typing import Optional,Union

class StudentCreate(BaseModel):
    first_name: str = Field(max_length=200, min_length=1)
    last_name: str = Field(max_length=200, min_length=1)
    email: EmailStr
    enrollment_date: date


class InstructorCreate(BaseModel):
    first_name: str = Field(max_length=200, min_length=1)
    last_name: str = Field(max_length=200, min_length=1)
    email: EmailStr
    department_id: int
    
class CourseCreate(BaseModel):
    name: str = Field(max_length=200, min_length=1)
    credits: int
    department_id: int


class StudentUpdate(BaseModel):
    first_name: Optional[str] = Field(max_length=200, min_length=1)
    last_name: Optional[str] = Field(max_length=200, min_length=1)
    email: EmailStr
    enrollment_date: date


class CourseUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200, min_length=1)
    credits: int
    department_id: int


class InstructorUpdate(BaseModel):
    first_name: Optional[str] = Field(max_length=200, min_length=1)
    last_name: Optional[str] = Field(max_length=200, min_length=1)
    email: EmailStr
    department_id: int

class AverageGradeResponse(BaseModel):
    student_id: int
    average_grade: Optional[float]

class InstructorPatch(BaseModel):
    email: Optional[EmailStr] = None
    department_id: Optional[int] = None

