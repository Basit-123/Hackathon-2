# Tasks: Authentication

**Input**: Design documents from `specs/002-authentication/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), requirements.md

**Tests**: Unit tests for JWT verification, integration tests for signup/signin flows

**Organization**: Tasks are grouped by authentication phases

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- Backend code: `backend/`
- Middleware: `backend/middleware.py`
- Configuration: `backend/config.py`
- Models: `backend/models.py`

---

## Phase 1: Foundation (Backend Setup)

**Purpose**: Initialize FastAPI project, configure Better Auth, install dependencies

- [ ] T001 [P] Initialize FastAPI project structure
- [ ] T002 [P] Install required dependencies (better-auth, python-jose, python-multipart)
- [ ] T003 [P] Create `backend/config.py` with environment variable loading
- [ ] T004 [P] Configure BETTER_AUTH_SECRET and DATABASE_URL in config
- [ ] T005 [US3] Create `backend/main.py` with FastAPI app initialization

**Checkpoint**: Foundation complete - FastAPI project ready

---

## Phase 2: Better Auth Configuration (User Story 1-2)

**Purpose**: Configure Better Auth for user management and JWT issuance

- [ ] T006 [US1] Configure Better Auth in `backend/main.py`
- [ ] T007 [US1] Setup Better Auth JWT plugin with BETTER_AUTH_SECRET
- [ ] T008 [US1] Configure Better Auth users table (auto-managed)
- [ ] T009 [US1] Configure JWT token expiration time (7 days recommended)
- [ ] T010 [US1] Implement Better Auth signup route (if not built-in)
- [ ] T011 [US2] Implement Better Auth signin route (if not built-in)

**Checkpoint**: Better Auth configured - signup/signin available

---

## Phase 3: JWT Verification Middleware (User Story 3)

**Purpose**: Implement middleware to verify JWT on all requests

- [ ] T012 [US3] Create `backend/middleware.py` with JWT verification logic
- [ ] T013 [US3] Implement Authorization header extraction
- [ ] T014 [US3] Implement JWT decoding using BETTER_AUTH_SECRET
- [ ] T015 [US3] Extract user_id from valid JWT token
- [ ] T016 [US3] Attach user_id to request.state
- [ ] T017 [US3] Return 401 Unauthorized for invalid/expired tokens
- [ ] T018 [US3] Integrate middleware into FastAPI app in `main.py`

**Checkpoint**: Middleware complete - JWT verification active on all routes

---

## Phase 4: User ID Matching (User Story 3)

**Purpose**: Ensure JWT user_id matches URL path user_id

- [ ] T019 [US3] Implement user_id matching logic in middleware
- [ ] T020 [US3] Return 401 Unauthorized on user_id mismatch
- [ ] T021 [US3] Test middleware with valid/invalid tokens
- [ ] T022 [US3] Test user_id matching scenario (token user_id vs URL user_id)

**Checkpoint**: user_id matching complete - multi-user isolation enforced

---

## Phase 5: Testing & Validation (User Story 1-3)

**Purpose**: Verify all authentication flows work correctly

- [ ] T023 [US1] Test signup with valid email/password
- [ ] T024 [US1] Test signup with duplicate email (expect error)
- [ ] T025 [US2] Test signin with valid credentials (expect JWT)
- [ ] T026 [US2] Test signin with invalid password (expect error)
- [ ] T027 [US3] Test JWT verification with valid token
- [ ] T028 [US3] Test JWT verification with expired token (expect 401)
- [ ] T029 [US3] Test user_id mismatch (expect 401)

**Checkpoint**: Authentication tested - all flows validated

---

## Phase 6: Documentation

**Purpose**: Create runtime guidance and documentation

- [ ] T030 [P] Create `backend/CLAUDE.md` with FastAPI patterns and JWT middleware usage
- [ ] T031 [P] Document BETTER_AUTH_SECRET requirements and generation
- [ ] T032 [P] Document environment variable setup (DATABASE_URL, BETTER_AUTH_SECRET)

**Checkpoint**: Documentation complete - guidance available

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundation (Phase 1)**: No dependencies - can start immediately
- **Better Auth (Phase 2)**: Depends on Foundation completion
- **Middleware (Phase 3)**: Depends on Phase 2 (Better Auth configured)
- **User ID Matching (Phase 4)**: Depends on Phase 3 (middleware complete)
- **Testing (Phase 5)**: Depends on Phase 4 (user_id matching complete)
- **Documentation (Phase 6)**: Can run in parallel with Phase 5

### Within Each Phase

- All Phase 1 tasks marked [P] can run in parallel
- All Phase 2 tasks sequential (T006 → T007 → ... → T011)
- All Phase 3 tasks sequential (T012 → T013 → ... → T018)
- All Phase 4 tasks sequential (T019 → T020 → ... → T022)
- All Phase 5 tasks sequential (T023 → T024 → ... → T029)
- T030, T031, T032 can run in parallel (Phase 6)

### Parallel Opportunities

- **Group 1**: T001, T002, T003, T004, T005, T030, T031, T032 can all run in parallel (Foundation + documentation)
- **Group 2**: T006, T010, T011 can run in parallel after Phase 1 (Better Auth routes)
- **Group 3**: T012, T013, T014, T015 can run in parallel with T016, T017 (JWT decoding vs response)

---

## Implementation Strategy

### Sequential Flow

1. Complete Phase 1: Foundation (FastAPI setup)
2. Complete Phase 2: Better Auth configuration
3. Complete Phase 3: JWT middleware implementation
4. Complete Phase 4: user_id matching logic
5. Complete Phase 5: Testing all authentication flows
6. Complete Phase 6: Documentation (can be done in parallel)

### Core Security Requirement

All API routes (created in `@specs/003-backend-task-crud/`) will depend on:
- JWT verification middleware from Phase 3
- user_id matching from Phase 4

---

## Notes

- JWT middleware is critical for security - must be implemented before any task routes
- BETTER_AUTH_SECRET must be at least 32 characters and stored securely
- All 401 responses must include clear error messages
- Better Auth manages users table - no manual user table needed
