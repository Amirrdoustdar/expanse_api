from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import database, crud, auth, models, schemas

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/monthly")
def monthly_report(year: int, month: int,
                   db: Session = Depends(database.get_db),
                   current_user: models.User = Depends(auth.get_current_user)):
    """Get monthly expense report"""
    return crud.get_monthly_report(db, current_user.id, year, month)

@router.get("/yearly", response_model=schemas.YearlyReportResponse)
def yearly_report(year: int,
                  db: Session = Depends(database.get_db),
                  current_user: models.User = Depends(auth.get_current_user)):
    """Get yearly expense report"""
    return crud.get_yearly_report(db, current_user.id, year)

@router.get("/summary")
def expense_summary(db: Session = Depends(database.get_db),
                   current_user: models.User = Depends(auth.get_current_user)):
    """Get expense summary"""
    expenses = crud.get_expenses(db, current_user.id)
    total = sum(expense.amount for expense in expenses)
    return {
        "total_expenses": len(expenses),
        "total_amount": total,
        "average_expense": total / len(expenses) if expenses else 0
    }