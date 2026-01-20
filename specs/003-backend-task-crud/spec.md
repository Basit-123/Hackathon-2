# Feature Specification: Backend Task CRUD

**Feature Branch**: `003-backend-task-crud`
**Created**: 2025-01-11
**Status**: Draft
**Input**: User description: "FastAPI REST API for task CRUD operations with JWT verification and multi-user isolation"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create Task (Priority: P1)

User needs to create new tasks via API.

**Why this priority**: Core functionality - without task creation, users cannot store todo items. This is the first action most users will perform.

**Independent Test**: Can be tested by making POST request with task data and verifying task is created in database.

**Acceptance Scenarios**:

1. **Given** authenticated user has valid JWT token, **When** user makes POST request to `/api/{user_id}/tasks` with JSON body `{"title": "Buy groceries", "description": "Get milk and eggs"}`, **Then** task is created in database with user_id from token
2. **Given** request includes empty title, **When** POST request is made, **Then** system returns 400 Bad Request with error message "Title is required"
3. **Given** user_id from JWT is "user123", **When** POST request to `/api/user123/tasks` succeeds, **Then** task's user_id field is set to "user123"
4. **Given** task is created successfully, **When** POST response is returned, **Then** response includes task id and status code 201 Created

---

### User Story 2 - List Tasks (Priority: P1)

User needs to view all their tasks with optional filtering and sorting.

**Why this priority**: Primary display requirement - users must see their tasks to manage them. This is the most frequently used API endpoint.

**Independent Test**: Can be tested by making GET request and verifying task list is returned with correct filtering and sorting.

**Acceptance Scenarios**:

1. **Given** user has 5 tasks (3 active, 2 completed), **When** user makes GET request to `/api/{user_id}/tasks`, **Then** all 5 tasks are returned in response
2. **Given** user has mixed tasks, **When** user adds query param `status=active`, **Then** only 3 active tasks are returned
3. **Given** user has mixed tasks, **When** user adds query param `status=completed`, **Then** only 2 completed tasks are returned
4. **Given** user has multiple tasks, **When** user adds query param `sort_by=created_at`, **Then** tasks are sorted by creation date (newest first)
5. **Given** user has multiple tasks, **When** user adds query param `sort_by=title`, **Then** tasks are sorted alphabetically by title
6. **Given** user_id from JWT is "user123", **When** GET request to `/api/user123/tasks` is made, **Then** only tasks with user_id="user123" are returned

---

### User Story 3 - Get Single Task (Priority: P2)

User needs to retrieve details of a specific task.

**Why this priority**: Enables detailed task editing and viewing - users may need to see full description before modifying.

**Independent Test**: Can be tested by making GET request with task id and verifying correct task details are returned.

**Acceptance Scenarios**:

1. **Given** user has task with id=42, **When** user makes GET request to `/api/{user_id}/tasks/42`, **Then** task details for id=42 are returned
2. **Given** user tries to get task with id=999 that doesn't exist, **When** GET request is made, **Then** system returns 404 Not Found
3. **Given** user has task with id=42, **When** user A (who owns task) makes GET request, **Then** task is returned successfully
4. **Given** user B (different user) tries to get user A's task id=42, **When** GET request is made to `/api/userB/tasks/42`, **Then** system returns 404 Not Found (or 401 if implementation prefers that)

---

### User Story 4 - Update Task (Priority: P2)

User needs to modify existing task title and description.

**Why this priority**: Enhances usability - users often need to correct typos or add details after initial creation.

**Independent Test**: Can be tested by making PUT request with updated data and verifying changes persist.

**Acceptance Scenarios**:

1. **Given** user has task with id=42 with title "Buy groceries", **When** user makes PUT request to `/api/{user_id}/tasks/42` with JSON body `{"title": "Buy groceries and milk", "description": "Get milk, eggs, and bread"}`, **Then** task is updated in database
2. **Given** task is updated successfully, **When** PUT response is returned, **Then** response includes updated task details and status code 200 OK
3. **Given** user tries to update task id=999 that doesn't exist, **When** PUT request is made, **Then** system returns 404 Not Found
4. **Given** user has task id=42, **When** user updates with empty title, **Then** system returns 400 Bad Request with "Title is required"

---

### User Story 5 - Delete Task (Priority: P2)

User needs to remove tasks they no longer need.

**Why this priority**: Essential for task management - users accumulate completed or obsolete tasks that need cleanup.

**Independent Test**: Can be tested by making DELETE request and verifying task no longer exists in database.

**Acceptance Scenarios**:

1. **Given** user has task with id=42, **When** user makes DELETE request to `/api/{user_id}/tasks/42`, **Then** task is removed from database
2. **Given** task is deleted successfully, **When** DELETE response is returned, **Then** status code is 204 No Content
3. **Given** user tries to delete task id=999 that doesn't exist, **When** DELETE request is made, **Then** system returns 404 Not Found
4. **Given** user has deleted task, **When** user makes GET request to `/api/{user_id}/tasks/42`, **Then** system returns 404 Not Found

---

### User Story 6 - Toggle Task Completion (Priority: P1)

User needs to mark tasks as completed or reactivate completed tasks.

**Why this priority**: Primary workflow - the core purpose of a Todo list is to track completion progress.

**Independent Test**: Can be tested by making PATCH request and verifying task completed status updates.

**Acceptance Scenarios**:

1. **Given** user has active task with id=42 (completed=false), **When** user makes PATCH request to `/api/{user_id}/tasks/42/complete`, **Then** task status changes to completed=true
2. **Given** user has completed task with id=42 (completed=true), **When** user makes PATCH request to `/api/{user_id}/tasks/42/complete`, **Then** task status changes to completed=false (reactivated)
3. **Given** task completion is toggled successfully, **When** PATCH response is returned, **Then** response includes updated task with new completed status and status code 200 OK
4. **Given** user tries to toggle task id=999 that doesn't exist, **When** PATCH request is made, **Then** system returns 404 Not Found

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide POST endpoint `/api/{user_id}/tasks` for creating tasks
- **FR-002**: System MUST require title field in task creation request
- **FR-003**: System MUST accept optional description field in task creation request
- **FR-004**: System MUST set completed=false by default on new task creation
- **FR-005**: System MUST return 201 Created status on successful task creation
- **FR-006**: System MUST return 400 Bad Request when title is missing
- **FR-007**: System MUST provide GET endpoint `/api/{user_id}/tasks` for listing tasks
- **FR-008**: System MUST support query parameter `status` with values `active` or `completed` for filtering tasks
- **FR-009**: System MUST support query parameter `sort_by` with values `created_at` or `title` for sorting tasks
- **FR-010**: System MUST provide GET endpoint `/api/{user_id}/tasks/{id}` for retrieving single task
- **FR-011**: System MUST return 404 Not Found for non-existent task ids
- **FR-012**: System MUST provide PUT endpoint `/api/{user_id}/tasks/{id}` for updating tasks
- **FR-013**: System MUST accept updates to title and description fields via PUT endpoint
- **FR-014**: System MUST provide DELETE endpoint `/api/{user_id}/tasks/{id}` for deleting tasks
- **FR-015**: System MUST return 204 No Content on successful deletion
- **FR-016**: System MUST provide PATCH endpoint `/api/{user_id}/tasks/{id}/complete` for toggling task completion status
- **FR-017**: System MUST toggle completed status between true and false on PATCH endpoint
- **FR-018**: All endpoints MUST verify JWT token from Authorization header
- **FR-019**: All endpoints MUST validate user_id from JWT matches user_id in URL path
- **FR-020**: All endpoints MUST return 401 Unauthorized for invalid/expired JWT tokens
- **FR-021**: All endpoints MUST return 401 Unauthorized when user_id from JWT does not match URL user_id

### Key Entities

- **Task**: Todo item with fields: id (integer PK), user_id (string FK to users table), title (string, required), description (string, optional), completed (boolean, default false), created_at (datetime), updated_at (datetime)
- **User**: Managed by Better Auth with email, password hash, and user_id

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: POST /api/{user_id}/tasks completes successfully in under 200ms
- **SC-002**: GET /api/{user_id}/tasks returns user's tasks in under 300ms
- **SC-003**: Filtering by status updates list in under 100ms
- **SC-004**: Sorting by date or title works correctly for all users
- **SC-005**: GET /api/{user_id}/tasks/{id} returns task in under 100ms
- **SC-006**: PUT /api/{user_id}/tasks/{id} updates task in under 200ms
- **SC-007**: DELETE /api/{user_id}/tasks/{id} removes task in under 200ms
- **SC-008**: PATCH /api/{user_id}/tasks/{id}/complete toggles status in under 200ms
- **SC-009**: Invalid JWT tokens are rejected with 401 status in under 50ms
- **SC-010**: User_id mismatch between token and URL returns 401 status in under 50ms

## Non-Functional Requirements *(optional)*

### Performance

- All API endpoints must respond in under 300ms (p95 latency)
- System must support 1000 concurrent users without degradation

### Security

- All endpoints must require JWT authentication
- All database queries must filter by user_id
- SQL injection protection via SQLModel ORM
- XSS protection not required (API-only, no HTML rendering)

### Reliability

- API uptime must be 99%+
- Database connection pooling must handle 50 concurrent connections

## Dependencies *(optional)*

- **Authentication**: Requires `@specs/002-authentication/spec.md` JWT verification middleware to be implemented
- **Database**: Requires Neon PostgreSQL database with users table (Better Auth) and tasks table
- **Constitution**: Must comply with `@specs/000-constitution/spec.md` security and multi-user isolation requirements

## Assumptions *(optional)*

- Neon PostgreSQL database is accessible via DATABASE_URL environment variable
- BETTER_AUTH_SECRET is available as environment variable
- Better Auth has created users table in database
- Frontend includes JWT token in Authorization header

## Edge Cases *(optional)*

- **EC-001**: What happens when user has zero tasks? → GET request returns empty array `[]`
- **EC-002**: What happens when sort_by parameter has invalid value? → Ignore filter and return default sort (created_at)
- **EC-003**: What happens when status parameter has invalid value? → Ignore filter and return all tasks
- **EC-004**: What happens if JWT token is malformed? → Return 401 Unauthorized immediately
- **EC-005**: What happens if user_id in URL is not a string? → Return 400 Bad Request with "Invalid user_id format"
- **EC-006**: What happens if task description is very long (>1000 chars)? → Accept it (no limit), or return 400 with "Description too long" if desired

## Change Log *(mandatory)*

| Version | Date | Changes | Author |
|---------|--------|----------|---------|
| 1.0.0 | 2025-01-11 | Initial backend task CRUD specification with all CRUD operations, JWT verification, and multi-user isolation | Claude Code |
