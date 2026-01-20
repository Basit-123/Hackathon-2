# Authentication Runtime Guidance

**Purpose**: Development guidelines for Better Auth JWT integration in FastAPI backend

## Tech Stack (from @specs/000-constitution/spec.md)

- **Backend Framework**: FastAPI
- **Language**: Python (3.10+)
- **Database**: PostgreSQL (Neon)
- **Authentication**: Better Auth with JWT

## Better Auth Setup

### Installation

```bash
pip install better-auth python-jose[cryptography] python-multipart
```

### Configuration

Configure in `backend/config.py`:

```python
from better_auth import BetterAuth
import os

auth = BetterAuth(
    secret=os.getenv("BETTER_AUTH_SECRET"),
    db_url=os.getenv("DATABASE_URL")
)
```

### JWT Plugin Setup

Better Auth provides JWT plugin out of the box. Configure token settings:

```python
# In backend/main.py
from better_auth import BetterAuth
from better_auth.jwt import JWT

auth = BetterAuth(
    secret=os.getenv("BETTER_AUTH_SECRET"),
    jwt={"secret": os.getenv("BETTER_AUTH_SECRET")}
)
```

## User Management

### Users Table

Better Auth creates users table automatically. Schema includes:
- `id`: User identifier (string)
- `email`: Email address (unique)
- `password_hash`: Hashed password
- `created_at`: Timestamp

### No Manual User Model Needed

Better Auth handles all user CRUD operations. Don't create custom User model in `models.py`.

## JWT Token Format

### Token Payload

JWT contains:
```json
{
  "user_id": "string",
  "exp": "timestamp"
}
```

### Token Issuance

Better Auth automatically issues JWT token on successful signin/signup.

## JWT Verification Middleware

### Middleware Location

Create in `backend/middleware.py` and import in `main.py`:

```python
from fastapi import Request
from better_auth.jwt import decode_token

async def verify_jwt(request: Request):
    # Extract token from Authorization header
    # Verify and decode token
    # Extract user_id
    # Attach to request.state
```

### Middleware Integration

Add to FastAPI app in `main.py`:

```python
from fastapi import FastAPI
from middleware import verify_jwt

app = FastAPI()
app.middleware("http")(verify_jwt)
```

## Protected Routes

### Apply Middleware Globally

Middleware runs on ALL requests. For public routes (health checks), add exceptions:

```python
from fastapi import HTTPException

async def verify_jwt(request: Request):
    if request.url.path == "/health":
        return  # Skip verification
    # ... rest of verification logic
```

### Access user_id in Routes

After middleware verification, access `user_id` from `request.state`:

```python
@app.get("/api/{user_id}/tasks")
async def get_tasks(user_id: str, request: Request):
    # user_id is also available via: request.state.user_id
    # Both should match if middleware validated correctly
    pass
```

## Security Requirements (from @specs/000-constitution/spec.md)

### MUST:

1. **JWT Verification on ALL requests** (except public routes)
2. **user_id from JWT must match user_id in URL** (`/api/{user_id}/tasks`)
3. **Return 401 Unauthorized** for:
   - Missing Authorization header
   - Invalid JWT token
   - Expired JWT token
   - user_id mismatch

### Token Security

- BETTER_AUTH_SECRET must be at least 32 characters
- Use cryptographically strong secret (random string, not dictionary word)
- Never commit BETTER_AUTH_SECRET to repository
- Use environment variables only

## Common Patterns

### Better Auth Signup/Signin Routes

Better Auth provides built-in routes. Configure in `main.py`:

```python
from better_auth import BetterAuth

app = FastAPI()
auth = BetterAuth(...)

# Better Auth automatically adds signup/signin routes
app.include_router(auth.router)
```

### Manual Routes (if needed)

If Better Auth doesn't provide desired endpoints, create manually:

```python
@app.post("/signup")
async def signup(email: str, password: str):
    # Use Better Auth user creation
    user = await auth.create_user(email, password)
    # Better Auth issues JWT token
    token = await auth.signin_user(email, password)
    return {"token": token}
```

## Error Handling

### 401 Unauthorized Response

Return consistent error format:

```python
from fastapi import HTTPException

raise HTTPException(
    status_code=401,
    detail="Invalid or expired JWT token"
)
```

### user_id Mismatch

```python
if user_id_from_token != user_id_from_url:
    raise HTTPException(
        status_code=401,
        detail="Unauthorized: user_id mismatch"
    )
```

## Environment Variables

Required in backend deployment:

- `BETTER_AUTH_SECRET`: Shared secret for JWT signing/validation
- `DATABASE_URL`: Neon PostgreSQL connection string

### Example .env

```bash
BETTER_AUTH_SECRET=your-secret-key-min-32-chars
DATABASE_URL=postgresql://user:password@host/database
```

## Development Workflow

1. **Configure Better Auth**: Setup in `backend/main.py` and `backend/config.py`
2. **Implement Middleware**: Create `backend/middleware.py` with JWT verification
3. **Integrate Middleware**: Add to FastAPI app in `main.py`
4. **Test Flows**:
   - Signup → Verify JWT issued
   - Signin → Verify JWT issued
   - API request with valid JWT → Should succeed
   - API request with invalid JWT → Should return 401
   - API request with user_id mismatch → Should return 401

## Common Pitfalls

**Avoid**:
- Implementing manual user management (use Better Auth)
- Hardcoding JWT tokens
- Skipping JWT verification on any route
- Returning user_id in API responses (security risk)

**Use Instead**:
- Better Auth for all user operations
- JWT verification middleware on ALL requests
- Environment variables for secrets
- user_id from request.state (validated by middleware)
