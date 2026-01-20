# Tasks: Frontend Todo UI

**Input**: Design documents from `specs/001-frontend-todo-ui/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), requirements.md

**Tests**: Component tests optional (can be added in Phase 5 - Testing & Validation)

**Organization**: Tasks are grouped by user story phases

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- Frontend code: `frontend/`
- Components: `frontend/components/`
- Pages: `frontend/app/`
- API client: `frontend/lib/`
- Configuration: `frontend/`

---

## Phase 1: Foundation (Setup)

**Purpose**: Initialize Next.js project, configure Tailwind, install dependencies

- [x] T001 [P] Initialize Next.js 16+ project with TypeScript and Tailwind CSS
- [x] T002 [P] Install Better Auth dependencies (better-auth)
- [x] T003 [P] Create root layout with basic structure
- [x] T004 [P] Create root page redirecting to signin or tasks

**Checkpoint**: Foundation complete - Next.js project ready for development

---

## Phase 2: API Client Development

**Purpose**: Create centralized API client with JWT handling

- [x] T005 [US1] Create `frontend/lib/api.ts` with base API configuration and helper functions
- [x] T006 [US1] Implement JWT token storage in localStorage
- [x] T007 [US1] Implement Authorization: Bearer <token> header in API client
- [x] T008 [US1] Implement 401 Unauthorized handling (redirect to signin)
- [x] T009 [US1] Implement GET request helper for `/api/{user_id}/tasks` with query params
- [x] T010 [US1] Implement POST request helper for creating tasks
- [x] T011 [US1] Implement PUT request helper for updating tasks
- [x] T012 [US1] Implement DELETE request helper for deleting tasks
- [x] T013 [US1] Implement PATCH request helper for toggling task completion

**Checkpoint**: API client complete - all task CRUD operations available

---

## Phase 3: Authentication Pages (User Story 6)

**Purpose**: Create Better Auth signup and signin UI pages

- [x] T014 [US6] Create `frontend/app/signup/page.tsx` with Better Auth signup form
- [x] T015 [US6] Create `frontend/app/signin/page.tsx` with Better Auth signin form
- [x] T016 [US6] Configure Better Auth server actions in `frontend/app/api/auth/`
- [x] T017 [US6] Implement signup success handling (redirect to signin)
- [x] T018 [US6] Implement signin success handling (store JWT, redirect to tasks)

**Checkpoint**: Authentication pages complete - users can signup/signin

---

## Phase 4: Protected Route Middleware (User Story 6)

**Purpose**: Ensure unauthenticated users cannot access protected pages

- [x] T019 [US6] Create `frontend/middleware.ts` with route protection logic
- [x] T020 [US6] Implement JWT token check on protected routes
- [x] T021 [US6] Implement redirect to signin for missing/invalid tokens
- [x] T022 [US6] Configure protected route patterns (e.g., /tasks/*)

**Checkpoint**: Middleware complete - protected routes require authentication

---

## Phase 5: Task List Page (User Story 1)

**Purpose**: Create Server Component for displaying tasks with filtering and sorting

- [x] T023 [US1] Create `frontend/app/tasks/page.tsx` as Server Component
- [x] T024 [US1] Implement server-side data fetching for tasks using API client
- [x] T025 [US1] Implement task filtering by status (active/completed)
- [x] T026 [US1] Implement task sorting (created_at/title)
- [x] T027 [US1] Create responsive Tailwind layout for task list
- [x] T028 [US1] Implement empty state message ("Create your first task")
- [x] T029 [US1] Implement loading state skeleton

**Checkpoint**: Task list page complete - users can view their tasks

---

## Phase 6: Task Form Component (User Story 2)

**Purpose**: Create Client Component for creating/editing tasks

- [x] T030 [US2] Create `frontend/components/TaskForm.tsx` as Client Component
- [x] T031 [US2] Implement form with title and description fields
- [x] T032 [US2] Implement title validation (required field)
- [x] T033 [US2] Implement form submission via API client
- [x] T034 [US2] Implement success handling (clear form, update list)
- [x] T035 [US2] Implement error handling and display

**Checkpoint**: Task form complete - users can create tasks

---

## Phase 7: Task Item Component (User Stories 3-5)

**Purpose**: Create Client Component for displaying and managing individual tasks

- [x] T036 [US3] Create `frontend/components/TaskItem.tsx` as Client Component
- [x] T037 [US3] Implement task display (title, description, completed status)
- [x] T038 [US3] Implement edit button and modal/form
- [x] T039 [US4] Implement delete button with confirmation
- [x] T040 [US5] Implement complete button (toggle status)
- [x] T041 [US3] Implement visual feedback for completed status (strikethrough/color change)
- [x] T042 [US3] Implement edit mode with form prepopulation
- [x] T043 [US4] Implement delete confirmation dialog
- [x] T044 [US5] Implement toggle animation for completion status

**Checkpoint**: Task item component complete - users can manage tasks

---

## Phase 8: Polish & Validation

**Purpose**: Create CLAUDE.md and verify responsive design

- [x] T045 [P] Create `frontend/CLAUDE.md` with Next.js patterns and API client guidance
- [ ] T046 [US1] Test task list on mobile viewport (min 375px width)
- [ ] T047 [US1] Test task list on tablet viewport (768px width)
- [ ] T048 [US1] Test task list on desktop viewport (1024px+ width)
- [ ] T049 [P] Verify all user stories work end-to-end

**Checkpoint**: Feature complete - frontend Todo UI ready for integration

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundation (Phase 1)**: No dependencies - can start immediately
- **API Client (Phase 2)**: Depends on Foundation completion
- **Authentication Pages (Phase 3)**: Depends on Foundation completion, can start in parallel with Phase 2
- **Middleware (Phase 4)**: Depends on Phase 2 (API client) and Phase 3 (Better Auth configured)
- **Task List Page (Phase 5)**: Depends on Phase 2 (API client) and Phase 4 (middleware)
- **Task Form (Phase 6)**: Depends on Phase 2 (API client)
- **Task Item (Phase 7)**: Depends on Phase 2 (API client)
- **Polish (Phase 8)**: Depends on all previous phases

### Within Each Phase

- All Phase 1 tasks marked [P] can run in parallel
- All Phase 2 tasks sequential (T005 → T006 → ... → T013)
- All Phase 3 tasks sequential (T014 → T015 → ... → T018)
- All Phase 4 tasks sequential (T019 → T020 → ... → T022)
- All Phase 5 tasks sequential (T023 → T024 → ... → T029)
- All Phase 6 tasks sequential (T030 → T031 → ... → T035)
- All Phase 7 tasks sequential (T036 → T037 → ... → T044)
- T045, T049 can run in parallel with other tasks in Phase 8

### Parallel Opportunities

- **Group 1**: T001, T002, T003, T004, T045 can all run in parallel (Phase 1 + early setup)
- **Group 2**: T014, T015 can run in parallel with T005 after Phase 1 (Phase 3 start with Phase 2)
- **Group 3**: T030, T036 can run in parallel after Phase 2 complete (Phase 6 & 7 can start together)
- **Group 4**: T046, T047, T048 can run in parallel (Phase 8 responsive testing)

---

## Implementation Strategy

### Foundation First

1. Complete Phase 1: Initialize Next.js project with dependencies
2. Complete Phase 2: Build API client with JWT handling
3. Complete Phase 3 & 4: Better Auth integration + protected routes

### Core Features

1. Complete Phase 5: Task list page (Server Component)
2. Complete Phase 6: Task form (Client Component)
3. Complete Phase 7: Task item (Client Component) with all actions

### Polish

1. Complete Phase 8: CLAUDE.md + responsive testing
2. End-to-end verification of all user stories

---

## Notes

- All API requests go through centralized `frontend/lib/api.ts` client
- JWT token is stored in localStorage for MVP simplicity
- Server Components used for initial data fetch, Client Components for interactivity
- Tailwind CSS provides mobile-first responsive design
