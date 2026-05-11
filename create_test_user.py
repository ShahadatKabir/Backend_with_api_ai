#!/usr/bin/env python3

from sqlalchemy.orm import Session
from core.database import SessionLocal, engine
from models.user import User
from utils.auth import get_password_hash

def create_test_user():
    # Create database tables if they don't exist
    User.__table__.create(bind=engine, checkfirst=True)

    # Create a test user
    db = SessionLocal()
    try:
        # Check if test user already exists
        existing_user = db.query(User).filter(User.email == "test@example.com").first()
        if existing_user:
            print("Test user already exists!")
            return

        # Create new test user
        hashed_password = get_password_hash("pass123")  # Shorter password
        test_user = User(
            email="test@example.com",
            hashed_password=hashed_password,
            is_active=True
        )

        db.add(test_user)
        db.commit()
        db.refresh(test_user)

        print("✅ Test user created successfully!")
        print("📧 Email: test@example.com")
        print("🔒 Password: pass123")
        print("\nYou can now login at: POST /auth/token")
        print("Use these credentials in the request body:")
        print("username: test@example.com")
        print("password: pass123")

    except Exception as e:
        print(f"Error creating user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()