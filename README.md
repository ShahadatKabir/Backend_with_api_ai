# My Project: Simple API + Web App

## What is this project?

This project is a small web application and API built to manage items in a simple system.

The main goal is to show how a real application can:
- let a user log in,
- store data in a database,
- create and manage items,
- expose that data through an API,
- and also show a simple web interface for users.

In simple words: this project helps us understand how an API is created, how it works, and why it is useful in real software.

---

## What is the purpose of the project?

The purpose is to learn and practice how to build a backend system that:
- receives requests from a browser or app,
- checks who the user is,
- reads or writes data,
- and returns a response.

This is useful because most modern applications use APIs. For example:
- a website asks the backend for data,
- a mobile app fetches products,
- a dashboard shows reports,
- a system updates records in the database.

This project is a simple example of that flow.

---

## What I used in this project and where

### 1. Python
Python is the main programming language used to build this project.

Where it is used:
- backend logic
- API routes
- database logic
- user authentication

### 2. FastAPI
FastAPI is the framework used to create the API.

Why it is used:
- it is fast,
- it is easy to build APIs with it,
- it creates automatic API documentation,
- it helps us create routes like login, get items, create items, update items, delete items.

Where it is used:
- main.py
- routes/

### 3. SQLAlchemy
This helps the project talk to the SQLite database.

Why it is used:
- it helps us save and fetch data easily,
- it connects Python code to database tables,
- it keeps the project organized.

Where it is used:
- models/
- core/database.py

### 4. SQLite
This is the database used here.

Why it is used:
- it is simple,
- it is lightweight,
- it works well for small projects,
- no extra database server is needed.

Where it is used:
- app.db

### 5. Pydantic
Pydantic validates data.

Example:
- checking if email is in the correct format,
- checking if required fields are provided,
- making sure the request body is valid.

Where it is used:
- schemas/

### 6. Jinja2 templates and HTML
This project also has a website UI.

Why it is used:
- to show pages like login, dashboard, and items,
- to create a simple front-end without a heavy frontend framework.

Where it is used:
- templates/
- static/

### 7. JWT / Auth
JWT is used for login and user authentication.

Why it is used:
- it helps verify who the user is,
- it gives permission to access protected routes,
- it keeps the app secure.

Where it is used:
- utils/auth.py
- routes/auth.py

---

## What I did in this project

I created a small full-stack project that includes:
- a login system,
- a dashboard,
- an item list page,
- item creation and editing,
- item deletion,
- API routes,
- database support,
- and a simple UI.

The project allows us to:
- register/login a user,
- see an overview of items,
- create new items,
- update them,
- delete them,
- view everything through the API and the website.

---

## How this project is running

The project runs using a Python server called Uvicorn.

The app starts from the file:
- main.py

When the server starts, it:
1. loads the FastAPI application,
2. sets up routes,
3. creates the database tables,
4. starts listening for requests on a local URL,
5. waits for browser or API calls.

The app runs locally at:
- http://127.0.0.1:8000

It also provides API docs here:
- http://127.0.0.1:8000/docs

This is very helpful because we can test the API from a browser without writing extra tools.

---

## How this helps us as we are creating an API

This project is useful because it shows the full lifecycle of an API:

### Step 1: User sends a request
A user opens the website or uses the API and asks for something.

Example:
- login
- get all items
- create item
- delete item

### Step 2: API receives the request
FastAPI reads the request and finds the matching route.

Example:
- POST /items/create
- GET /api/v1/items/

### Step 3: Validation happens
The system checks whether the data is valid.

Example:
- email is correct,
- title is provided,
- item data is in the expected format.

### Step 4: Database is used
The server sends the request to the SQLite database.

Example:
- add a new item,
- fetch list of items,
- update item details,
- remove an item.

### Step 5: Response is returned
The server sends back a response to the user.

This could be:
- HTML page,
- JSON data,
- success message,
- error message.

This is the basic idea of an API.

---

## How API is created here in very simple terms

Think of the API like a waiter in a restaurant.

- The user asks for something.
- The API (waiter) takes the request.
- It goes to the kitchen (backend code).
- The kitchen checks the database or logic.
- Then it brings back the result.

In this project:
- the browser or user sends a request,
- FastAPI matches that request to a route,
- the code performs the action,
- the database stores or retrieves data,
- and the response is sent back.

So an API is simply a way for programs to talk to each other in a structured and reliable way.

---

## Simple example

If we want to create an item:

1. User fills a form in the website.
2. Browser sends the data to the backend.
3. FastAPI route receives it.
4. Server validates the data.
5. Data is saved in the SQLite database.
6. Response is returned: success or error.

This is how many real applications work.

---

## Project structure (simple view)

```text
api/
├── main.py              # Starts the application
├── routes/              # API routes
├── models/              # Database tables
├── schemas/             # Data validation
├── core/                # Database and settings
├── utils/               # Login and auth helpers
├── templates/           # HTML pages for the website
├── static/              # CSS and JavaScript files
├── app.db               # SQLite database
├── requirements.txt     # Project dependencies
└── README.md            # Project documentation
```

---

## How to run this project

1. Open terminal in the project folder.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the app:

```bash
uvicorn main:app --reload
```

4. Open in browser:
- http://127.0.0.1:8000
- API documentation: http://127.0.0.1:8000/docs

---

## Why this project is useful

This project helps us understand:
- how APIs are built,
- how users log in,
- how data is saved,
- how frontend and backend connect,
- how real-world applications are structured.

It is a strong beginner-friendly example of a working API project.

---

## Final summary

This project is a simple API and web app built using Python and FastAPI. It helps us manage items in a database, support login, and show how backend logic works in a real system.

The main idea is simple:
- user sends a request,
- API receives it,
- backend processes it,
- database stores data,
- response returns to the user.

This is exactly how many modern applications work in the real world.

