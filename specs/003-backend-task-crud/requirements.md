# Backend Task CRUD Requirements

**Purpose**: High-level requirements for FastAPI Task CRUD API with user isolation

## What We Need

The backend needs to provide REST API for task management with:

1. **Task Model**
   - Task entity with id, user_id FK, title, description, completed, timestamps
   - User table managed by Better Auth

2. **Task CRUD Operations**
   - Create task for user
   - List all tasks for user with filtering and sorting
   - Get single task by id
   - Update task
   - Delete task
   - Toggle completion status

3. **Security & Isolation**
   - JWT verification on all requests
   - User_id from JWT must match URL user_id
   - All queries filter by user_id

4. **API Contract**
   - RESTful endpoints under `/api/{user_id}/tasks`
   - JSON request/response format
   - Proper HTTP status codes

## Success Criteria

- All CRUD operations work with user isolation
- Invalid/missing JWT returns 401
- User_id mismatch returns 401
- Filtering and sorting work correctly
