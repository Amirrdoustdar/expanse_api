from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, extract, and_
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import calendar
from . import models, schemas, auth


def create_user(db: Session, user: schemas.UserCreate):
    hashed_pw = auth.get_password_hash(user.password)  # Use get_password_hash
    db_user = models.User(username=user.username, hashed_password=hashed_pw)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    db_user = db.query(models.User).filter(models.User.username == username).first()
    if not db_user or not auth.verify_password(password, db_user.hashed_password):
        return None
    return db_user

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_expense(db: Session, user_id: int, expense: schemas.ExpenseCreate):
    db_expense = models.Expense(**expense.dict(), user_id=user_id)
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

def get_expense(db: Session, expense_id: int, user_id: int):
    return db.query(models.Expense).filter(
        models.Expense.id == expense_id,
        models.Expense.user_id == user_id
    ).first()

def get_expenses(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Expense)
        .filter(models.Expense.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def update_expense(db: Session, expense_id: int, user_id: int, updated: schemas.ExpenseUpdate):
    expense = get_expense(db, expense_id, user_id)
    if expense:
        for key, value in updated.dict(exclude_unset=True).items():
            setattr(expense, key, value)
        db.commit()
        db.refresh(expense)
    return expense

def delete_expense(db: Session, expense_id: int, user_id: int):
    expense = get_expense(db, expense_id, user_id)
    if expense:
        db.delete(expense)
        db.commit()
    return expense

def create_category(db: Session, category: schemas.CategoryCreate, user_id: int):
    db_category = models.Category(**category.dict(), user_id=user_id)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_categories(db: Session, user_id: int):
    return db.query(models.Category).filter(models.Category.user_id == user_id).all()


def get_category(db: Session, category_id: int, user_id: int):
    """Get a specific category by ID for a user"""
    return db.query(models.Category).filter(
        models.Category.id == category_id,
        models.Category.user_id == user_id
    ).first()

def update_category(db: Session, category_id: int, user_id: int, category_update: schemas.CategoryBase):
    """Update a category"""
    category = get_category(db, category_id, user_id)
    if category:
        for key, value in category_update.dict(exclude_unset=True).items():
            setattr(category, key, value)
        db.commit()
        db.refresh(category)
    return category

def delete_category(db: Session, category_id: int, user_id: int):
    """Delete a category"""
    category = get_category(db, category_id, user_id)
    if category:
        # Check if category has expenses
        has_expenses = db.query(models.Expense).filter(
            models.Expense.category_id == category_id
        ).first()
        
        if has_expenses:
            # Set expenses to uncategorized instead of deleting
            db.query(models.Expense).filter(
                models.Expense.category_id == category_id
            ).update({models.Expense.category_id: None})
        
        db.delete(category)
        db.commit()
    return category

def get_monthly_report(db: Session, user_id: int, year: int, month: int):
    # Simple implementation - you can enhance this
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(days=1)
    
    total = db.query(func.sum(models.Expense.amount)).filter(
        models.Expense.user_id == user_id,
        models.Expense.created_at >= start_date,
        models.Expense.created_at <= end_date
    ).scalar() or 0
    
    count = db.query(func.count(models.Expense.id)).filter(
        models.Expense.user_id == user_id,
        models.Expense.created_at >= start_date,
        models.Expense.created_at <= end_date
    ).scalar() or 0
    
    return {
        "year": year,
        "month": month,
        "total_amount": total,
        "expense_count": count
    }
def get_yearly_report(db: Session, user_id: int, year: int) -> schemas.YearlyReportResponse:
    start_date = datetime(year, 1, 1)
    end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    
    # Total for the year
    total_amount = db.query(func.sum(models.Expense.amount)).filter(
        models.Expense.user_id == user_id,
        models.Expense.created_at >= start_date,
        models.Expense.created_at <= end_date
    ).scalar() or 0.0
    
    # Monthly breakdown
    monthly_query = db.query(
        extract('month', models.Expense.created_at).label('month'),
        func.sum(models.Expense.amount).label('total')
    ).filter(
        models.Expense.user_id == user_id,
        models.Expense.created_at >= start_date,
        models.Expense.created_at <= end_date
    ).group_by(extract('month', models.Expense.created_at)).all()
    
    monthly_breakdown = {}
    for month_num, total in monthly_query:
        month_name = calendar.month_name[int(month_num)]
        monthly_breakdown[month_name] = float(total)
    
    # Top categories
    category_query = db.query(
        models.Category.name,
        models.Category.color,
        func.sum(models.Expense.amount).label('total'),
        func.count(models.Expense.id).label('count')
    ).join(
        models.Expense, models.Category.id == models.Expense.category_id
    ).filter(
        models.Expense.user_id == user_id,
        models.Expense.created_at >= start_date,
        models.Expense.created_at <= end_date
    ).group_by(models.Category.id).order_by(func.sum(models.Expense.amount).desc()).limit(5).all()
    
    top_categories = []
    for cat_name, cat_color, cat_total, cat_count in category_query:
        percentage = (cat_total / total_amount * 100) if total_amount > 0 else 0
        top_categories.append(schemas.CategoryExpense(
            category_name=cat_name,
            category_color=cat_color,
            total_amount=cat_total,
            expense_count=cat_count,
            percentage=round(percentage, 2)
        ))
    
    return schemas.YearlyReportResponse(
        year=year,
        total_expenses=total_amount,
        monthly_breakdown=monthly_breakdown,
        top_categories=top_categories
    )


def get_expenses_for_export(db: Session, user_id: int, start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None, categories: Optional[List[int]] = None):
    query = db.query(models.Expense).options(joinedload(models.Expense.category)).filter(
        models.Expense.user_id == user_id
    )
    
    if start_date:
        query = query.filter(models.Expense.created_at >= start_date)
    
    if end_date:
        query = query.filter(models.Expense.created_at <= end_date)
    
    if categories:
        query = query.filter(models.Expense.category_id.in_(categories))
    
    return query.order_by(models.Expense.created_at.desc()).all()