# Implementation Plan: Backend Task CRUD

**Branch**: `003-backend-task-crud` | **Date**: 2025-01-11 | **Spec**: @specs/003-backend-task-crud/spec.md
**Input**: Feature specification from `specs/003-backend-task-crud/spec.md`

## Summary

Implement FastAPI REST API for task CRUD operations with JWT verification middleware and multi-user isolation per constitution security requirements.

## Technical Context

**Language/Version**: Python (3.10+) | **Framework**: FastAPI | **ORM**: SQLModel |
**Database**: PostgreSQL (Neon) | **Authentication**: JWT (via @specs/002-authentication/spec.md) |
**Primary Dependencies**: fastapi, uvicorn, sqlmodel, psycopg2-binary, better-auth (for users table) |
**Target Platform**: Server (API endpoints) | **Project Type**: REST API |
**Performance Goals**: < 300ms per endpoint (p95), 1000 concurrent users | **Constraints**: Multi-user isolation via user_id filtering |
**Scale/Scope**: 6 user stories (create, list, get, update, delete, toggle completion), 7 REST endpoints |

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Check against constitution**:
- [x] Spec references @specs/000-constitution/spec.md
- [x] Tech stack uses FastAPI, SQLModel, Neon PostgreSQL
- [x] JWT verification middleware referenced (from @specs/002-authentication/spec.md)
- [x] All endpoints use /api/{user_id}/tasks pattern
- [x] user_id from JWT must match URL user_id (401 on mismatch)
- [x] All queries filter by user_id (multi-user isolation)
- [x] No alternative frameworks without justification

**Result**: ✅ PASS - All gates satisfied

## Project Structure

### Backend Code (target)

```text
backend/
├── main.py                      # FastAPI app with routes and middleware
├── models.py                      # Task model (SQLModel)
├── db.py                         # Database connection and session
├── routes/
│   ├── __init__.py
│   └── tasks.py                 # Task CRUD endpoints
├── middleware.py                  # JWT verification (from @specs/002-authentication/)
└── CLAUDE.md                     # Runtime guidance
```

### Database Schema

```text
users (Better Auth managed)
├── id (string PK)
├── email (string, unique)
├── password_hash (string)
└── created_at (datetime)

tasks
├── id (int PK, auto-increment)
├── user_id (string FK -> users.id)
├── title (string, required)
├── description (string, optional)
├── completed (boolean, default false)
├── created_at (datetime, default now)
└── updated_at (datetime, auto-update)

Indexes:
- idx_user_id on (user_id)
- idx_user_completed on (user_id, completed)
```

### API Endpoints

| Method | Path | Description | Auth |
|--------|------|-------------|-------|
| POST | /api/{user_id}/tasks | Create task | JWT |
| GET | /api/{user_id}/tasks | List tasks | JWT |
| GET | /api/{user_id}/tasks/{id} | Get single task | JWT |
| PUT | /api/{user_id}/tasks/{id} | Update task | JWT |
| DELETE | /api/{user_id}/tasks/{id} | Delete task | JWT |
| PATCH | /api/{user_id}/tasks/{id}/complete | Toggle completion | JWT |

## Key Decisions

1. **Task Model Design**
   - SQLModel for type safety and auto-validation
   - Integer primary key (auto-increment) for simple ordering
   - String user_id (foreign key) to match Better Auth users table

2. **user_id Filtering**
   - All queries include `WHERE user_id = ?` parameter
   - Middleware extracts user_id from JWT token
   - user_id in URL must match user_id from JWT (security requirement)

3. **Query Parameters**
   - status: Optional filter (active/completed) → `WHERE completed = ?`
   - sort_by: Optional sort (created_at/title) → `ORDER BY ?`

4. **Index Strategy**
   - Index on user_id for fast user isolation queries
   - Composite index on (user_id, completed) for filtering performance

## Architecture Overview

### Request Flow

```text
Client Request
    ↓
JWT Verification Middleware (@specs/002-authentication/)
    ├─ Invalid/Expired → Return 401
    └─ Valid → Extract user_id
        ↓
    Attach user_id to request.state
        ↓
    Route Handler (tasks.py)
        ↓
    Verify user_id matches URL path
        ├─ Mismatch → Return 401
        └─ Match → Process request
            ↓
        Query Database (SQLModel)
            ↓
        Return Response
```

### Data Flow (Create Task Example)

```text
POST /api/user123/tasks
    ↓
JWT Middleware: Verify token, extract user_id="user123"
    ↓
Route: Check user_id (token) == user_id (URL)? Yes
    ↓
Validation: Check title not empty
    ↓
DB Insert: INSERT INTO tasks (user_id, title, description, completed, ...)
    ↓
Response: Return 201 Created with task id and details
```

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| user_id in URL path | Constitution requirement: /api/{user_id}/tasks pattern | /api/tasks with user_id in token is simpler but violates constitution |
| JWT middleware dependency | Required per constitution security requirements | Inline token check in every route is error-prone and harder to maintain |
