from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import csv
import io
import pandas as pd
from .. import database, crud, auth, schemas

router = APIRouter(prefix="/export", tags=["export"])

@router.get("/csv")
def export_csv(start_date: Optional[datetime] = None,
               end_date: Optional[datetime] = None,
               categories: Optional[str] = None,
               db: Session = Depends(database.get_db),
               current_user=Depends(auth.get_current_user)):
    
    # Parse categories if provided
    category_list = None
    if categories:
        try:
            category_list = [int(x) for x in categories.split(',')]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid categories format")
    
    # Get expenses
    expenses = crud.get_expenses_for_export(db, current_user.id, start_date, end_date, category_list)
    
    # Create CSV content
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['ID', 'Description', 'Amount', 'Category', 'Date'])
    
    # Write data
    for expense in expenses:
        category_name = expense.category.name if expense.category else 'Uncategorized'
        writer.writerow([
            expense.id,
            expense.description or '',
            expense.amount,
            category_name,
            expense.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    output.seek(0)
    
    filename = f"expenses_{current_user.username}_{datetime.now().strftime('%Y%m%d')}.csv"
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/excel")
def export_excel(start_date: Optional[datetime] = None,
                end_date: Optional[datetime] = None,
                categories: Optional[str] = None,
                db: Session = Depends(database.get_db),
                current_user=Depends(auth.get_current_user)):
    
    # Parse categories if provided
    category_list = None
    if categories:
        try:
            category_list = [int(x) for x in categories.split(',')]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid categories format")
    
    # Get expenses
    expenses = crud.get_expenses_for_export(db, current_user.id, start_date, end_date, category_list)
    
    # Create DataFrame
    data = []
    for expense in expenses:
        category_name = expense.category.name if expense.category else 'Uncategorized'
        data.append({
            'ID': expense.id,
            'Description': expense.description or '',
            'Amount': expense.amount,
            'Category': category_name,
            'Date': expense.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    df = pd.DataFrame(data)
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Expenses', index=False)
        
        # Add summary sheet
        summary_data = {
            'Total Expenses': [len(expenses)],
            'Total Amount': [sum(expense.amount for expense in expenses)],
            'Date Range': [f"{start_date or 'All'} to {end_date or 'All'}"]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    output.seek(0)
    
    filename = f"expenses_{current_user.username}_{datetime.now().strftime('%Y%m%d')}.xlsx"
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )