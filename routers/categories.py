from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, crud, database, auth, models

router = APIRouter(prefix="/categories", tags=["categories"])

@router.post("/", response_model=schemas.Category)
def create_category(category: schemas.CategoryCreate,
                    db: Session = Depends(database.get_db),
                    current_user: models.User = Depends(auth.get_current_user)):
    """Create a new category"""
    return crud.create_category(db, category, current_user.id)

@router.get("/", response_model=List[schemas.Category])
def get_categories(db: Session = Depends(database.get_db),
                   current_user: models.User = Depends(auth.get_current_user)):
    """Get user's categories"""
    return crud.get_categories(db, current_user.id)

@router.get("/{category_id}", response_model=schemas.Category)
def get_category(category_id: int,
                 db: Session = Depends(database.get_db),
                 current_user: models.User = Depends(auth.get_current_user)):
    """Get a specific category"""
    category = crud.get_category(db, category_id, current_user.id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.put("/{category_id}", response_model=schemas.Category)
def update_category(category_id: int,
                    category_update: schemas.CategoryBase,
                    db: Session = Depends(database.get_db),
                    current_user: models.User = Depends(auth.get_current_user)):
    """Update a category"""
    category = crud.update_category(db, category_id, current_user.id, category_update)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.delete("/{category_id}")
def delete_category(category_id: int,
                    db: Session = Depends(database.get_db),
                    current_user: models.User = Depends(auth.get_current_user)):
    """Delete a category"""
    category = crud.delete_category(db, category_id, current_user.id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted successfully"}