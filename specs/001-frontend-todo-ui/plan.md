# Implementation Plan: Frontend Todo UI

**Branch**: `001-frontend-todo-ui` | **Date**: 2025-01-11 | **Spec**: @specs/001-frontend-todo-ui/spec.md
**Input**: Feature specification from `specs/001-frontend-todo-ui/spec.md`

## Summary

Create Next.js 16+ frontend with responsive Task List UI, authentication pages, API client with JWT integration, and comprehensive task management features.

## Technical Context

**Language/Version**: TypeScript (Next.js 16+) | **Framework**: Next.js 16+ App Router | **Styling**: Tailwind CSS |
**Primary Dependencies**: better-auth, @better-auth/react (Better Auth UI), @tanstack/react-query (optional for data fetching) |
**Storage**: localStorage for JWT tokens | **State Management**: React useState/useEffect (no complex state needed) |
**Target Platform**: Web browsers (Chrome, Firefox, Safari, Edge) | **Project Type**: Single Page Application |
**Performance Goals**: Page load < 2s, API responses < 500ms | **Constraints**: Mobile-first responsive design, JWT token security |
**Scale/Scope**: 6 user stories, task list with filtering/sorting, authentication, CRUD operations |

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Check against constitution**:
- [x] Spec references @specs/000-constitution/spec.md
- [x] Tech stack uses Next.js 16+ App Router, TypeScript, Tailwind CSS
- [x] Better Auth JWT integration specified
- [x] JWT token storage and handling described
- [x] API client includes Authorization Bearer header
- [x] 401 Unauthorized handling specified
- [x] Multi-user isolation via API (user_id in URL)
- [x] No alternative frameworks without justification

**Result**: ✅ PASS - All gates satisfied

## Project Structure

### Frontend Code (target)

```text
frontend/
├── app/
│   ├── page.tsx                 # Landing/redirect to signin
│   ├── signin/
│   │   └── page.tsx             # Better Auth signin form
│   ├── signup/
│   │   └── page.tsx             # Better Auth signup form
│   ├── tasks/
│   │   ├── page.tsx               # Server Component: task list
│   │   └── loading.tsx            # Loading skeleton
│   ├── api/
│   │   └── auth/
│   │       ├── [...]                # Better Auth server actions
│   └── layout.tsx               # Root layout
├── components/
│   ├── TaskForm.tsx               # Client Component: create/edit task
│   ├── TaskItem.tsx               # Client Component: single task display
│   └── TaskList.tsx               # Client Component: list container
├── lib/
│   └── api.ts                   # API client with JWT handling
├── middleware.ts                 # Route protection middleware
├── CLAUDE.md                    # Runtime guidance
└── package.json
```

### Key Decisions

1. **Server vs Client Components**
   - Task list page (Server Component): Fetches data server-side for SEO and initial render
   - Task form, Task item (Client Components): Interactive (forms, buttons)

2. **JWT Token Storage**
   - localStorage for MVP simplicity
   - Future: Consider httpOnly cookies for enhanced security

3. **API Client Design**
   - Centralized in lib/api.ts
   - Includes Authorization: Bearer <token> header automatically
   - Handles 401 responses with redirect to signin

4. **Responsive Design**
   - Mobile-first approach (Tailwind mobile: classes)
   - Breakpoints: sm:640px, md:768px, lg:1024px, xl:1280px

## Architecture Overview

### Data Flow

```text
User Action → Client Component → API Client (lib/api.ts)
                          ↓
                   Add JWT header (Authorization: Bearer <token>)
                          ↓
                   Send to Backend API
                          ↓
                   Response → Update State → Re-render UI
```

### Authentication Flow

```text
User visits /signin → Better Auth UI (signup/signin forms)
                    ↓
              Submit credentials
                    ↓
              Better Auth server action → Better Auth issues JWT token
                    ↓
              Frontend stores token in localStorage
                    ↓
              Redirect to /tasks → Middleware validates token exists
                    ↓
              Tasks page loads → API client includes JWT in all requests
```

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Client-side JWT storage | Simpler MVP implementation | Server-side cookies require more complex setup; localStorage acceptable for hackathon timeline |
