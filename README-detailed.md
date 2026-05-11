# Easy-to-Understand Guide to Our FastAPI Project

Hello! This guide will explain our FastAPI project in very simple terms. We'll go through each part of the code, file by file, and explain what everything does. No coding experience needed – we'll break it down like telling a story.

## What's This Project?

This is a simple API (Application Programming Interface) built with FastAPI. An API is like a waiter in a restaurant – it takes requests from customers (apps) and brings back data from the kitchen (database). Our API manages "items" (like products) and has user login.

## Project Structure

Our project is organized like this:
```
api/
├── main.py                 # Main app file
├── requirements.txt        # List of needed libraries
├── core/                   # Core settings and database setup
│   ├── config.py
│   └── database.py
├── models/                 # Database table definitions
│   ├── item.py
│   ├── user.py
│   └── __init__.py
├── schemas/                # Data validation rules
│   ├── item.py
│   ├── user.py
│   └── __init__.py
├── routes/                 # API endpoint definitions
│   ├── auth.py
│   ├── items.py
│   └── __init__.py
└── utils/                  # Helper functions
    └── auth.py
```

## Step 1: Installing What We Need

### requirements.txt

This file lists all the libraries (pre-made code) we need. Think of it as a shopping list.

```txt
fastapi==0.104.1          # The main framework for our API
uvicorn[standard]==0.24.0  # Server to run our app
sqlalchemy==2.0.23         # Tool to talk to database
alembic==1.13.1            # Database migration tool
python-jose[cryptography]==3.3.0  # For creating secure tokens
passlib[bcrypt]==1.7.4     # For password encryption
python-multipart==0.0.6    # For handling file uploads
pydantic==2.5.0            # For data validation
pydantic-settings==2.1.0   # For reading settings from files
```

To install: `pip install -r requirements.txt`

## Step 2: Setting Up the Database

### core/database.py

This file sets up how we connect to our database (SQLite, a simple file-based database).

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import settings

DATABASE_URL = settings.database_url  # Where our database file is

engine = create_engine(  # Creates the connection to database
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  # Creates database sessions

Base = declarative_base()  # Base class for our database tables

def get_db():  # Function that gives us a database connection
    db = SessionLocal()
    try:
        yield db  # Gives the connection
    finally:
        db.close()  # Closes the connection when done
```

### core/config.py

This file manages our settings, like database location and secret keys.

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./app.db"  # Default database file
    secret_key: str = "your-secret-key"        # Secret for encryption
    algorithm: str = "HS256"                   # Encryption method
    access_token_expire_minutes: int = 30      # Token lasts 30 minutes

    class Config:
        env_file = ".env"  # Read settings from .env file

settings = Settings()  # Create settings object
```

## Step 3: Defining Our Data Models

### models/item.py

This defines what an "Item" looks like in our database.

```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from core.database import Base

class Item(Base):  # Our Item table
    __tablename__ = "items"  # Table name in database

    id = Column(Integer, primary_key=True, index=True)  # Unique ID, auto-increases
    title = Column(String, index=True)                  # Item name
    description = Column(String)                        # Item details
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # When created
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())        # When updated
```

### models/user.py

This defines what a "User" looks like for login.

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from core.database import Base

class User(Base):  # Our User table
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)     # Unique email
    hashed_password = Column(String)                     # Encrypted password
    is_active = Column(Boolean, default=True)            # Is user active?
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

### models/__init__.py

This just imports our models so other files can use them.

```python
from .item import Item
from .user import User
from core.database import Base
```

## Step 4: Data Validation Schemas

### schemas/item.py

These are rules for what data is allowed when creating/updating items.

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ItemBase(BaseModel):  # Basic item fields
    title: str
    description: Optional[str] = None  # Optional field

class ItemCreate(ItemBase):  # For creating new items
    pass  # Same as ItemBase

class ItemUpdate(ItemBase):  # For updating items
    title: Optional[str] = None  # Title is optional in updates

class Item(ItemBase):  # Full item with all fields
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Can create from database objects
```

### schemas/user.py

Similar rules for user data.

```python
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr  # Must be valid email

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):  # For login response
    access_token: str
    token_type: str

class TokenData(BaseModel):  # Data inside tokens
    email: Optional[str] = None
```

## Step 5: Authentication Helpers

### utils/auth.py

Functions for login, password checking, and token creation.

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from core.database import get_db
from models.user import User
from schemas.user import TokenData
from core.config import settings

# Settings for passwords and tokens
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):  # Check if password matches
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):  # Encrypt password
    return pwd_context.hash(password)

def authenticate_user(db: Session, email: str, password: str):  # Check user credentials
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):  # Create login token
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):  # Get logged-in user
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user
```

## Step 6: API Routes (Endpoints)

### routes/auth.py

Handles user login.

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from core.database import get_db
from utils.auth import authenticate_user, create_access_token
from schemas.user import Token
from datetime import timedelta

router = APIRouter()  # Creates a group of routes

@router.post("/token", response_model=Token)  # POST /auth/token
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)  # Check login
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(  # Create token
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
```

### routes/items.py

Handles all item operations.

```python
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from models.item import Item
from schemas.item import Item as ItemSchema, ItemCreate, ItemUpdate
from utils.auth import get_current_user

router = APIRouter()

@router.get("/items/", response_model=List[ItemSchema])  # GET /api/v1/items/
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    items = db.query(Item).offset(skip).limit(limit).all()  # Get items with pagination
    return items

@router.post("/items/", response_model=ItemSchema)  # POST /api/v1/items/
def create_item(item: ItemCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    db_item = Item(**item.dict())  # Create new item
    db.add(db_item)
    db.commit()  # Save to database
    db.refresh(db_item)
    return db_item

@router.get("/items/{item_id}", response_model=ItemSchema)  # GET /api/v1/items/{id}
def read_item(item_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@router.put("/items/{item_id}", response_model=ItemSchema)  # PUT /api/v1/items/{id}
def update_item(item_id: int, item: ItemCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    for key, value in item.dict().items():  # Update all fields
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.patch("/items/{item_id}", response_model=ItemSchema)  # PATCH /api/v1/items/{id}
def partial_update_item(item_id: int, item: ItemUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    update_data = item.dict(exclude_unset=True)  # Only update provided fields
    for key, value in update_data.items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/items/{item_id}")  # DELETE /api/v1/items/{id}
def delete_item(item_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"detail": "Item deleted"}
```

### routes/__init__.py

Imports the route modules.

```python
from . import auth, items
```

## Step 7: Main Application

### main.py

This is where everything comes together – the main FastAPI app.

```python
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from core.database import engine
from models import item, user
from routes import auth, items

logging.basicConfig(level=logging.INFO)  # Set up logging
logger = logging.getLogger(__name__)

app = FastAPI(title="Professional API", version="1.0.0")  # Create the app

# Create database tables
item.Base.metadata.create_all(bind=engine)
user.Base.metadata.create_all(bind=engine)

# Add CORS middleware (allows web browsers to talk to our API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include our route groups
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(items.router, prefix="/api/v1", tags=["items"])

# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

@app.get("/")  # Simple welcome endpoint
def read_root():
    return {"message": "Welcome to the Professional API"}
```

## How to Run the Project

1. Install Python packages:
   ```
   pip install -r requirements.txt
   ```

2. Start the server:
   ```
   uvicorn main:app --reload
   ```

3. Visit `http://127.0.0.1:8000/docs` for interactive API documentation

## How to Use the API

1. **Login**: POST to `/auth/token` with username/password to get a token
2. **Use token**: Add `Authorization: Bearer <token>` header to requests
3. **Create items**: POST to `/api/v1/items/` with title and description
4. **List items**: GET `/api/v1/items/`
5. **Update items**: PUT or PATCH to `/api/v1/items/{id}`
6. **Delete items**: DELETE `/api/v1/items/{id}`

## Key Concepts Explained

- **FastAPI**: A modern web framework for building APIs
- **Pydantic**: Validates data to ensure it's correct
- **SQLAlchemy**: Helps us talk to the database
- **JWT**: JSON Web Tokens for secure authentication
- **REST**: Standard way of designing APIs
- **CRUD**: Create, Read, Update, Delete operations

That's it! Now you understand how our API works, piece by piece. Each function has a specific job, and they all work together to create a secure, scalable API.