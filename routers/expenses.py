from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from .. import schemas, crud, database, auth, models

router = APIRouter(prefix="/expenses", tags=["expenses"])

@router.post("/", response_model=schemas.ExpenseOut)
def create_expense(expense: schemas.ExpenseCreate,
                   db: Session = Depends(database.get_db),
                   current_user: models.User = Depends(auth.get_current_user)):
    """Create a new expense"""
    return crud.create_expense(db, current_user.id, expense)

@router.get("/", response_model=List[schemas.ExpenseOut])
def get_expenses(skip: int = Query(0, ge=0),
                limit: int = Query(100, ge=1, le=1000),
                db: Session = Depends(database.get_db),
                current_user: models.User = Depends(auth.get_current_user)):
    """Get user's expenses with pagination"""
    return crud.get_expenses(db, current_user.id, skip, limit)

@router.get("/{expense_id}", response_model=schemas.ExpenseOut)
def get_expense(expense_id: int,
                db: Session = Depends(database.get_db),
                current_user: models.User = Depends(auth.get_current_user)):
    """Get a specific expense"""
    expense = crud.get_expense(db, expense_id, current_user.id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense

@router.put("/{expense_id}", response_model=schemas.ExpenseOut)
def update_expense(expense_id: int,
                   expense_update: schemas.ExpenseUpdate,
                   db: Session = Depends(database.get_db),
                   current_user: models.User = Depends(auth.get_current_user)):
    """Update an expense"""
    expense = crud.update_expense(db, expense_id, current_user.id, expense_update)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense

@router.delete("/{expense_id}")
def delete_expense(expense_id: int,
                   db: Session = Depends(database.get_db),
                   current_user: models.User = Depends(auth.get_current_user)):
    """Delete an expense"""
    expense = crud.delete_expense(db, expense_id, current_user.id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": "Expense deleted successfully"}