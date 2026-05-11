# Professional FastAPI Project

This is a scalable, professional API built with FastAPI, following REST patterns and enterprise best practices with security-first approach.

## Features

- JWT Authentication
- CRUD operations for Items
- SQLite database
- Pydantic schemas for validation
- CORS middleware
- Error handling and logging
- Configurable settings

## Installation

1. Install all dependencies from requirements.txt:

   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

## API Endpoints

- `POST /auth/token` - Login
- `GET /api/v1/items/` - List items
- `POST /api/v1/items/` - Create item
- `GET /api/v1/items/{id}` - Get item
- `PUT /api/v1/items/{id}` - Update item
- `PATCH /api/v1/items/{id}` - Partial update item
- `DELETE /api/v1/items/{id}` - Delete item

All endpoints except login require authentication.

## Security

- JWT tokens for authentication
- Password hashing with bcrypt
- CORS enabled
- Input validation with Pydantic

## Database

Uses SQLite by default. To change, set `DATABASE_URL` in environment or .env file.

Tables are created automatically on startup.
