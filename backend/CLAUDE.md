# Backend Runtime Guidance

**Purpose**: Development guidelines for FastAPI Backend implementation

## Tech Stack (from @specs/000-constitution/spec.md)

- **Backend Framework**: FastAPI
- **Language**: Python (3.10+)
- **ORM**: SQLModel
- **Database**: PostgreSQL (Neon)
- **Authentication**: JWT (custom implementation with python-jose)

## Project Structure

```
backend/
├── main.py                      # FastAPI app initialization and router setup
├── config.py                     # Environment variable loading
├── db.py                         # Database connection and session management
├── models.py                      # SQLModel models (User, Task)
├── middleware.py                  # JWT verification middleware
├── routes/
│   ├── __init__.py
│   ├── auth.py                   # Authentication endpoints (signup/signin)
│   └── tasks.py                  # Task CRUD endpoints
├── requirements.txt               # Python dependencies
├── .env                          # Environment variables (local)
├── .env.example                  # Environment variable template
└── CLAUDE.md                     # This file
```

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create `.env` file:

```bash
DATABASE_URL=postgresql://user:password@host/database
BETTER_AUTH_SECRET=your-secret-key-min-32-characters-long
HOST=0.0.0.0
PORT=8000
```

### 3. Run the Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Or using python:

```bash
python main.py
```

API runs on `http://localhost:8000`

### 4. Access Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Database Models

### User Model

```python
class User(SQLModel, table=True):
    id: str                          # User identifier (email)
    email: str                       # Email address (unique)
    password_hash: str               # Bcrypt hashed password
    created_at: datetime              # Account creation timestamp
```

### Task Model

```python
class Task(SQLModel, table=True):
    id: int                          # Auto-increment primary key
    user_id: str                     # Foreign key to User.id
    title: str                       # Task title (required)
    description: str | None           # Optional description
    completed: bool                  # Completion status
    created_at: datetime              # Creation timestamp
    updated_at: datetime | None       # Last update timestamp
```

## API Endpoints

### Authentication Endpoints

#### POST /auth/signup
Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "secure123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

#### POST /auth/signin
Sign in an existing user.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "secure123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Task Endpoints

All task endpoints require JWT authentication and user isolation.

#### POST /api/{user_id}/tasks
Create a new task.

**Headers:**
```
Authorization: Bearer <token>
```

**Request:**
```json
{
  "title": "Buy groceries",
  "description": "Get milk and eggs"
}
```

**Response:** Task object with id (201 Created)

#### GET /api/{user_id}/tasks
List tasks with optional filtering and sorting.

**Query Parameters:**
- `status`: "active" | "completed" | omit (all)
- `sort_by`: "created_at" | "title"

**Response:** Array of Task objects

#### GET /api/{user_id}/tasks/{task_id}
Get a specific task.

**Response:** Task object (200 OK) or 404 Not Found

#### PUT /api/{user_id}/tasks/{task_id}
Update a task.

**Request:**
```json
{
  "title": "Updated title",
  "description": "Updated description"
}
```

**Response:** Updated Task object

#### DELETE /api/{user_id}/tasks/{task_id}
Delete a task.

**Response:** 204 No Content or 404 Not Found

#### PATCH /api/{user_id}/tasks/{task_id}/complete
Toggle task completion status.

**Response:** Updated Task object with flipped completed status

## JWT Authentication

### Token Format

JWT tokens contain:

```json
{
  "user_id": "user@example.com",
  "exp": 1234567890
}
```

### Token Verification

The middleware automatically:
1. Extracts token from `Authorization: Bearer <token>` header
2. Verifies token signature using BETTER_AUTH_SECRET
3. Checks token expiration
4. Extracts user_id from payload
5. Attaches user_id to `request.state`

### Accessing user_id in Routes

```python
from fastapi import Request

async def some_endpoint(user_id: str, request: Request):
    token_user_id = request.state.user_id
    # token_user_id should match user_id parameter
```

### User Isolation

Constitution requires:
- user_id from JWT must match user_id in URL path
- 401 Unauthorized returned on mismatch

Use the helper function:

```python
from middleware import verify_user_id_match

async def some_endpoint(user_id: str, request: Request):
    verify_user_id_match(request, user_id)
    # If user_ids don't match, returns 401 automatically
```

## Database Operations

### Getting a Session

Use dependency injection:

```python
from sqlmodel import Session
from db import get_session

async def my_endpoint(session: Session = Depends(get_session)):
    # Use session for database operations
    user = session.get(User, user_id)
    session.commit()
```

### Query Patterns

```python
from sqlmodel import select

# Single record by primary key
task = session.get(Task, task_id)

# Filter with conditions
tasks = session.exec(select(Task).where(Task.user_id == user_id)).all()

# Filter and sort
tasks = session.exec(
    select(Task)
    .where(Task.completed == False)
    .order_by(Task.created_at.desc())
).all()

# Count
count = session.exec(select(Task).where(Task.user_id == user_id)).one()
```

### Creating Records

```python
new_task = Task(
    user_id=user_id,
    title="My Task",
    description="Optional description",
    completed=False
)

session.add(new_task)
session.commit()
session.refresh(new_task)
```

### Updating Records

```python
task = session.get(Task, task_id)

if task:
    task.title = "Updated title"
    task.description = "Updated description"
    task.completed = not task.completed
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
```

### Deleting Records

```python
task = session.get(Task, task_id)

if task:
    session.delete(task)
    session.commit()
```

## Error Handling

### HTTPException

```python
from fastapi import HTTPException, status

# 400 Bad Request
raise HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Invalid input: title is required"
)

# 401 Unauthorized
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid or expired JWT token"
)

# 404 Not Found
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail=f"Task with id {task_id} not found"
)
```

### Response Format

Errors return JSON:

```json
{
  "detail": "Error message here"
}
```

## Password Hashing

### Hashing a Password

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

hashed_password = pwd_context.hash(plain_password)
```

### Verifying a Password

```python
is_valid = pwd_context.verify(plain_password, hashed_password)
```

## JWT Token Operations

### Creating a Token

```python
from jose import jwt
from datetime import datetime, timedelta

def create_access_token(user_id: str) -> str:
    expires_delta = timedelta(days=7)
    expire = datetime.utcnow() + expires_delta

    payload = {
        "user_id": user_id,
        "exp": expire,
    }

    token = jwt.encode(payload, BETTER_AUTH_SECRET, algorithm="HS256")
    return token
```

### Decoding a Token

```python
from jose import jwt

payload = jwt.decode(token, BETTER_AUTH_SECRET, algorithms=["HS256"])
user_id = payload["user_id"]
```

## Security Requirements

### MUST

1. **JWT Verification on ALL requests** (except auth endpoints)
2. **user_id from JWT must match URL path** (401 on mismatch)
3. **Return 401 Unauthorized** for:
   - Missing Authorization header
   - Invalid JWT token
   - Expired JWT token
   - user_id mismatch

### Token Security

- BETTER_AUTH_SECRET must be at least 32 characters
- Use cryptographically strong secret generation
- Never commit BETTER_AUTH_SECRET to repository
- Store in environment variables only

### Password Security

- Always hash passwords before storing (bcrypt)
- Never store plain text passwords
- Use passlib with bcrypt algorithm

## Testing

### Manual Testing with curl

**Signup:**
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "secure123"}'
```

**Signin:**
```bash
curl -X POST http://localhost:8000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "secure123"}'
```

**Create Task (replace TOKEN with actual token):**
```bash
curl -X POST http://localhost:8000/api/test@example.com/tasks \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "My First Task"}'
```

**Get Tasks:**
```bash
curl http://localhost:8000/api/test@example.com/tasks \
  -H "Authorization: Bearer TOKEN"
```

### Common Issues

**Database Connection Error:**
- Verify DATABASE_URL is correct
- Check Neon PostgreSQL is accessible
- Ensure database exists

**ImportError: No module named 'x':**
- Run `pip install -r requirements.txt`
- Check Python version (3.10+ required)

**401 Unauthorized:**
- Verify Authorization header is included
- Check token is valid (not expired)
- Ensure BETTER_AUTH_SECRET matches frontend

## Development Workflow

1. **Start**: Create models and schemas (models.py)
2. **Database**: Initialize tables (db.py - init_db())
3. **Middleware**: Implement JWT verification (middleware.py)
4. **Auth Routes**: Create signup/signin endpoints (routes/auth.py)
5. **Task Routes**: Implement CRUD with user isolation (routes/tasks.py)
6. **Test**: Use Swagger UI (/docs) or curl commands
7. **Integrate**: Test with frontend application

## Common Pitfalls

**Avoid:**
- Skipping JWT verification on any route
- Hardcoding secrets or URLs
- Not validating user_id matches JWT
- Exposing user_id in API responses
- Returning plain text passwords

**Use Instead:**
- Middleware for all protected routes
- Environment variables for all config
- verify_user_id_match() helper function
- Only return task details, not user information
- Always hash passwords with bcrypt
