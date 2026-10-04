from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session
from core.database import get_db
from models.item import Item
from schemas.item import Item as ItemSchema, ItemCreate, ItemUpdate
from utils.auth import get_current_user

router = APIRouter()


def apply_item_filters(query, search: str = ""):
    """Filter items by a case-insensitive search term across title and description."""
    term = (search or "").strip()
    if not term:
        return query
    like_term = f"%{term}%"
    return query.filter(or_(Item.title.ilike(like_term), Item.description.ilike(like_term)))


def apply_item_sorting(query, sort_by: str = "newest"):
    """Apply a sorting option to an item query."""
    sort_by = sort_by or "newest"
    sort_map = {
        "newest": query.order_by(Item.created_at.desc(), Item.id.desc()),
        "oldest": query.order_by(Item.created_at.asc(), Item.id.asc()),
        "title_asc": query.order_by(Item.title.asc(), Item.id.asc()),
        "title_desc": query.order_by(Item.title.desc(), Item.id.desc()),
    }
    return sort_map.get(sort_by, sort_map["newest"])


@router.get("/items/summary")
def read_items_summary(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    total_items = db.query(Item).count()
    recent_items = db.query(Item).filter(Item.created_at >= datetime.utcnow() - timedelta(days=7)).count()
    latest_item = db.query(Item).order_by(Item.created_at.desc()).first()
    return {
        "total_items": total_items,
        "recent_items": recent_items,
        "latest_item": {
            "id": latest_item.id,
            "title": latest_item.title,
        } if latest_item else None,
    }


@router.get("/items/", response_model=List[ItemSchema])
def read_items(skip: int = 0, limit: int = 100, search: str = "", sort_by: str = "newest", db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    items = apply_item_sorting(apply_item_filters(db.query(Item), search), sort_by).offset(skip).limit(limit).all()
    return items

@router.post("/items/", response_model=ItemSchema)
def create_item(item: ItemCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    db_item = Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/items/{item_id}", response_model=ItemSchema)
def read_item(item_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@router.put("/items/{item_id}", response_model=ItemSchema)
def update_item(item_id: int, item: ItemCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    for key, value in item.dict().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.patch("/items/{item_id}", response_model=ItemSchema)
def partial_update_item(item_id: int, item: ItemUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    update_data = item.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"detail": "Item deleted"}