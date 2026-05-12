# Professional FastAPI Project

This is a scalable, professional API built with FastAPI, following REST patterns and enterprise best practices with a security-first approach. Now includes a modern, responsive web interface!

## Features

### Backend
- JWT Authentication
- CRUD operations for Items
- SQLite database
- Pydantic schemas for validation
- CORS middleware
- Error handling and logging
- Configurable settings

### Frontend UI
- **Modern Dashboard** - Analytics and recent activity overview
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Dark Mode** - Toggle between light and dark themes
- **Authentication Pages** - Clean login interface
- **Item Management** - Full CRUD with list, create, edit, delete
- **Search & Filter** - Find items quickly
- **Pagination** - Handles large datasets
- **Toast Notifications** - Real-time feedback
- **Interactive Elements** - Hover effects, transitions, loading states
- **Professional Styling** - Tailwind CSS with custom design system

## Installation

1. Install all dependencies from requirements.txt:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

3. Open your browser and navigate to:
   - **Web UI Dashboard**: http://127.0.0.1:8000/dashboard
   - **API Documentation**: http://127.0.0.1:8000/docs

## UI/UX Features

### Dashboard
- View total items count and weekly statistics
- See recent items
- Quick access to common actions
- System status indicator

### Items Management
- Full list view with search
- Create/edit items via form
- Delete with confirmation
- Inline actions
- Pagination support

### Theme
- Light/Dark mode toggle
- Persists user preference
- Respects system preference by default

### Mobile Friendly
- Responsive navigation with hamburger menu
- Touch-friendly buttons and forms
- Optimized layouts for small screens

### User Experience
- Toast notifications for all actions
- Loading states
- Smooth transitions
- Empty states with guidance
- Form validation feedback

## API Endpoints

The backend still provides the full REST API:

- `POST /auth/token` - Login (JWT)
- `GET /api/v1/items/` - List items
- `POST /api/v1/items/` - Create item
- `GET /api/v1/items/{id}` - Get item
- `PUT /api/v1/items/{id}` - Update item
- `PATCH /api/v1/items/{id}` - Partial update
- `DELETE /api/v1/items/{id}` - Delete item

All endpoints except login require authentication.

## Security

- JWT tokens for authentication
- Password hashing with bcrypt
- CORS enabled
- Input validation with Pydantic
- Session-based flash messages
- CSRF protection ready

## Database

Uses SQLite by default. To change, set `DATABASE_URL` in environment or .env file.

Tables are created automatically on startup.

## Technology Stack

**Backend**: FastAPI, SQLAlchemy, SQLite, Pydantic, Python 3.14+

**Frontend**: Jinja2 Templates, Tailwind CSS, Vanilla JavaScript

**Design System**: Custom component library with cards, buttons, forms, tables, badgers, modals, dropdowns

## Project Structure

```
api/
├── main.py                 # Main app with UI routes
├── templates/              # Jinja2 HTML templates
│   ├── base.html          # Base layout
│   ├── login.html         # Login page
│   ├── dashboard.html     # Dashboard
│   ├── items.html         # Items list
│   └── item_form.html     # Create/Edit form
├── static/                # Static assets
│   ├── css/
│   │   └── styles.css    # Custom styles
│   └── js/
│       └── main.js       # Frontend logic
├── core/                  # Core configuration
├── models/                # Database models
├── schemas/               # Pydantic schemas
├── routes/                # API routes
├── utils/                 # Utilities
└── app.db                 # SQLite database
```

## Getting Started

### Using the Web UI

1. Start the server: `uvicorn main:app --reload`
2. Visit http://127.0.0.1:8000/login
3. Login with demo credentials or any user you create
4. Start managing your items through the UI

### Using the API directly

View interactive API docs at /docs or /redoc.
