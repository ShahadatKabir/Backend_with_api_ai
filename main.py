import logging
from datetime import datetime, timedelta

import uvicorn
from fastapi import FastAPI, Request, Depends, HTTPException, Form, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from core.database import engine, get_db
from models import item, user
from routes import auth, items
from utils.auth import get_current_user, get_password_hash
import secrets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Professional API", version="1.0.0")

# Add session middleware for flash messages
app.add_middleware(SessionMiddleware, secret_key=secrets.token_urlsafe(32))

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Create database tables
item.Base.metadata.create_all(bind=engine)
user.Base.metadata.create_all(bind=engine)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(items.router, prefix="/api/v1", tags=["items"])

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

@app.get("/")
def read_root():
    return {"message": "Welcome to the Professional API"}

# ===== UI ROUTES =====

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Render login page"""
    return templates.TemplateResponse("login.html", {
        "request": request,
        "current_user": None
    })

@app.post("/login", response_class=HTMLResponse)
async def login_handler(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Handle login form submission"""
    from utils.auth import authenticate_user, create_access_token
    
    user = authenticate_user(db, username, password)
    if not user:
        flash(request, "Invalid email or password", "error")
        return templates.TemplateResponse("login.html", {
            "request": request,
            "current_user": None,
        }, status_code=401)
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=1800,
        expires=1800,
        samesite="lax"
    )
    flash(response, "Login successful!", "success")
    return response

@app.get("/logout")
async def logout(request: Request):
    """Logout user"""
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("access_token")
    flash(response, "You have been logged out", "info")
    return response

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """Render dashboard page"""
    from models.item import Item
    
    current_user = await get_current_user(
        await request.cookies.get("access_token", "").replace("Bearer ", ""),
        db
    ) if await request.cookies.get("access_token") else None
    
    db_items = db.query(Item).order_by(Item.created_at.desc()).limit(5).all()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "current_user": current_user,
        "recent_items": db_items,
        "stats": {
            "total_items": db.query(Item).count(),
            "recent_count": db.query(Item).filter(
                Item.created_at >= datetime.utcnow() - timedelta(days=7)
            ).count()
        }
    })

@app.get("/items", response_class=HTMLResponse, name="items_list")
async def items_list_page(
    request: Request,
    page: int = 1,
    search: str = "",
    sort: str = "newest",
    db: Session = Depends(get_db)
):
    """Render items list page with pagination and search"""
    from models.item import Item
    from routes.items import apply_item_filters, apply_item_sorting
    
    current_user = await get_current_user(
        await request.cookies.get("access_token", "").replace("Bearer ", ""),
        db
    ) if await request.cookies.get("access_token") else None
    
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    
    per_page = 10
    query = db.query(Item)
    query = apply_item_filters(query, search)
    query = apply_item_sorting(query, sort)
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    total_pages = (total + per_page - 1) // per_page
    
    return templates.TemplateResponse("items.html", {
        "request": request,
        "current_user": current_user,
        "items": items,
        "page": page,
        "total_pages": total_pages,
        "total": total,
        "search": search,
        "sort_by": sort
    })

@app.get("/items/create", response_class=HTMLResponse, name="item_create")
@app.get("/items/{item_id}/edit", response_class=HTMLResponse, name="item_edit")
async def item_form_page(
    request: Request,
    item_id: int = None,
    db: Session = Depends(get_db)
):
    """Render item create/edit form"""
    from models.item import Item
    
    current_user = await get_current_user(
        await request.cookies.get("access_token", "").replace("Bearer ", ""),
        db
    ) if await request.cookies.get("access_token") else None
    
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    
    item = None
    if item_id:
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
            return RedirectResponse(url="/items", status_code=303)
    
    return templates.TemplateResponse("item_form.html", {
        "request": request,
        "current_user": current_user,
        "item": item
    })

@app.post("/items/create", name="item_store")
@app.post("/items/{item_id}/edit", name="item_update")
async def item_form_handler(
    request: Request,
    item_id: int = None,
    title: str = Form(...),
    description: str = Form(None),
    db: Session = Depends(get_db)
):
    """Handle item form submission"""
    from models.item import Item
    
    current_user = await get_current_user(
        await request.cookies.get("access_token", "").replace("Bearer ", ""),
        db
    ) if await request.cookies.get("access_token") else None
    
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    
    try:
        if item_id:
            item = db.query(Item).filter(Item.id == item_id).first()
            if item:
                item.title = title
                item.description = description
                flash(request, "Item updated successfully!", "success")
            else:
                flash(request, "Item not found", "error")
                return RedirectResponse(url="/items", status_code=303)
        else:
            item = Item(title=title, description=description)
            db.add(item)
            flash(request, "Item created successfully!", "success")
        
        db.commit()
        return RedirectResponse(url="/items", status_code=303)
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving item: {e}")
        flash(request, "Failed to save item", "error")
        return RedirectResponse(
            url=f"{'/items/create' if not item_id else f'/items/{item_id}/edit'}", 
            status_code=303
        )

@app.post("/items/{item_id}/delete")
async def delete_item_handler(
    request: Request,
    item_id: int,
    db: Session = Depends(get_db)
):
    """Handle item deletion"""
    from models.item import Item
    
    current_user = await get_current_user(
        await request.cookies.get("access_token", "").replace("Bearer ", ""),
        db
    ) if await request.cookies.get("access_token") else None
    
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    
    item = db.query(Item).filter(Item.id == item_id).first()
    if item:
        db.delete(item)
        db.commit()
        flash(request, "Item deleted successfully", "success")
    else:
        flash(request, "Item not found", "error")
    
    return RedirectResponse(url="/items", status_code=303)

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Custom 404 page"""
    return templates.TemplateResponse("404.html", {
        "request": request,
        "current_user": None
    }, status_code=404)

@app.get("/register", response_class=HTMLResponse, name="register")
async def register_page(request: Request):
    """Render registration page"""
    return templates.TemplateResponse("register.html", {
        "request": request,
        "current_user": None
    })

@app.post("/register", response_class=HTMLResponse)
async def register_handler(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    db: Session = Depends(get_db)
):
    """Handle registration form submission"""
    from models.user import User
    from utils.auth import get_password_hash
    
    # Validate passwords match
    if password != password_confirm:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "current_user": None,
            "error": "Passwords do not match"
        }, status_code=400)
    
    # Check if user exists
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "current_user": None,
            "error": "Email already registered"
        }, status_code=400)
    
    # Create user
    user = User(
        email=email,
        hashed_password=get_password_hash(password),
        is_active=True
    )
    db.add(user)
    db.commit()
    
    flash(request, "Registration successful! Please log in.", "success")
    return RedirectResponse(url="/login", status_code=303)

# Helper function for flash messages
def flash(request: Request, message: str, category: str = "info"):
    """Add a flash message to the session"""
    if "_messages" not in request.session:
        request.session["_messages"] = []
    request.session["_messages"].append({"message": message, "category": category})

def get_flashed_messages(request: Request, with_categories: bool = False):
    """Get and clear flash messages from session"""
    messages = request.session.pop("_messages", []) if "_messages" in request.session else []
    if with_categories:
        return [(msg["category"], msg["message"]) for msg in messages]
    return [msg["message"] for msg in messages]

# Make flash and get_flashed_messages available to templates
templates.env.globals["get_flashed_messages"] = get_flashed_messages


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)