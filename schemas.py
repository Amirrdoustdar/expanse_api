from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

# ========================
# User Schemas
# ========================

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel): 
    username: str
    password: str

class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True

# ========================
# Category Schemas
# ========================

class CategoryEnum(str, Enum):
    FOOD = "Food"
    UTILITIES = "Utilities"
    TRANSPORT = "Transport"
    ENTERTAINMENT = "Entertainment"
    HEALTHCARE = "Healthcare"
    SHOPPING = "Shopping"
    EDUCATION = "Education"
    OTHER = "Other"

class CategoryBase(BaseModel):
    name: str
    color: Optional[str] = "#3B82F6"  # Default blue color
    icon: Optional[str] = "📋"

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# ========================
# Expense Schemas
# ========================

class ExpenseBase(BaseModel):
    amount: float
    description: Optional[str] = None
    category_id: Optional[int] = None

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(BaseModel):
    amount: Optional[float] = None
    description: Optional[str] = None
    category_id: Optional[int] = None

class Expense(ExpenseBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    category: Optional[Category] = None

    class Config:
        from_attributes = True

# For backward compatibility
ExpenseOut = Expense

# ========================
# Report Schemas
# ========================

class CategoryExpense(BaseModel):
    category_name: str
    category_color: str
    total_amount: float
    expense_count: int
    percentage: float

class MonthlyReportResponse(BaseModel):
    year: int
    month: int
    total_expenses: float
    expense_count: int
    categories: List[CategoryExpense]
    daily_breakdown: dict

class YearlyReportResponse(BaseModel):
    year: int
    total_expenses: float
    monthly_breakdown: dict
    top_categories: List[CategoryExpense]

# ========================
# Export Schemas
# ========================

class ExportRequest(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    categories: Optional[List[int]] = None
    format: str = "csv"  # csv, excel, json

class ExportResponse(BaseModel):
    filename: str
    download_url: str
    total_records: int
    file_size: str