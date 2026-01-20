# Feature Specification: Deployment Setup

**Feature Branch**: `004-deployment-setup`
**Created**: 2025-01-11
**Status**: Draft
**Input**: User description: "Production deployment configuration for Todo app on Vercel (frontend), Render/Fly.io (backend), and Neon (database)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Frontend Deployment to Vercel (Priority: P2)

Frontend needs to be deployed to Vercel platform for public access.

**Why this priority**: Frontend must be accessible to users - Vercel is recommended platform for Next.js applications per constitution tech stack requirements.

**Independent Test**: Can be tested by connecting to deployed Vercel URL and verifying application loads.

**Acceptance Scenarios**:

1. **Given** frontend code is pushed to git repository, **When** Vercel deployment is triggered, **Then** Next.js application builds successfully
2. **Given** Vercel build is successful, **When** deployment completes, **Then** application is accessible at `https://<project-name>.vercel.app`
3. **Given** environment variable `NEXT_PUBLIC_API_URL` is configured, **When** application loads, **Then** frontend can connect to backend API
4. **Given** deployment fails during build, **When** error occurs, **Then** Vercel shows build logs for troubleshooting

---

### User Story 2 - Backend Deployment to Render/Fly.io (Priority: P2)

Backend needs to be deployed to Render or Fly.io platform for API access.

**Why this priority**: Backend API must be accessible to frontend - FastAPI deployment to cloud platform is required for production use.

**Independent Test**: Can be tested by making API requests to deployed URL and verifying endpoints respond correctly.

**Acceptance Scenarios**:

1. **Given** backend code is pushed to git repository, **When** Render/Fly.io deployment is triggered, **Then** FastAPI application builds successfully
2. **Given** backend is deployed, **When** deployment completes, **Then** API is accessible at `https://<project-name>.onrender.com` or similar
3. **Given** environment variables `DATABASE_URL` and `BETTER_AUTH_SECRET` are configured, **When** backend starts, **Then** database connection succeeds
4. **Given** backend is running, **When** API requests are made, **Then** endpoints return valid responses
5. **Given** environment variable is missing, **When** backend starts, **Then** application fails with clear error about missing variable

---

### User Story 3 - Neon Database Setup (Priority: P1)

Neon PostgreSQL database needs to be created and configured.

**Why this priority**: Database is fundamental dependency - without it, no data can be persisted. This must be done before any deployment.

**Independent Test**: Can be tested by connecting application to Neon database and verifying read/write operations work.

**Acceptance Scenarios**:

1. **Given** user has Neon account, **When** they create a new project, **Then** Neon provides connection string (DATABASE_URL)
2. **Given** DATABASE_URL is obtained, **When** it is configured in backend environment variables, **Then** backend can connect to database
3. **Given** backend connects successfully, **When** Better Auth creates users table, **Then** table is created in Neon PostgreSQL
4. **Given** database is connected, **When** SQLModel creates tasks table, **Then** table with correct schema is created in Neon PostgreSQL
5. **Given** database is connected, **When** user creates task via API, **Then** task is persisted to Neon PostgreSQL database

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide deployment configuration for Next.js frontend to Vercel platform
- **FR-002**: System MUST configure `NEXT_PUBLIC_API_URL` environment variable in Vercel
- **FR-003**: System MUST provide deployment configuration for FastAPI backend to Render or Fly.io platform
- **FR-004**: System MUST configure `DATABASE_URL` environment variable in backend deployment
- **FR-005**: System MUST configure `BETTER_AUTH_SECRET` environment variable in backend deployment (shared with frontend if applicable)
- **FR-006**: System MUST configure start command `uvicorn main:app --host 0.0.0.0 --port $PORT` for FastAPI backend
- **FR-007**: System MUST create Neon PostgreSQL project and provide connection string
- **FR-008**: System MUST document all required environment variables with descriptions
- **FR-009**: System MUST provide clear production URLs for frontend and backend after deployment

### Key Entities

- **Environment Variable**: Configuration value stored in deployment platform (e.g., `DATABASE_URL`, `BETTER_AUTH_SECRET`, `NEXT_PUBLIC_API_URL`)
- **Neon Project**: PostgreSQL database project on Neon cloud platform
- **Vercel Deployment**: Frontend hosting on Vercel platform with auto-SSL
- **Render/Fly.io Deployment**: Backend hosting on Render or Fly.io platform with auto-SSL

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Vercel deployment completes in under 5 minutes
- **SC-002**: Render/Fly.io deployment completes in under 5 minutes
- **SC-003**: Neon database is accessible in under 30 seconds
- **SC-004**: Frontend is accessible via HTTPS URL
- **SC-005**: Backend is accessible via HTTPS URL
- **SC-006**: All environment variables are configured correctly
- **SC-007**: End-to-end test (frontend → backend → database) completes successfully

## Non-Functional Requirements *(optional)*

### Performance

- Frontend must load in under 3 seconds on production
- Backend API must respond in under 500ms (p95)
- Database connection must be established in under 1 second

### Security

- All environment variables must be configured via deployment platform (never hardcoded)
- `BETTER_AUTH_SECRET` must be at least 32 characters and use cryptographically strong generation
- All production traffic must use HTTPS (automatic on Vercel, Render, Fly.io)
- DATABASE_URL must not be logged or exposed in application responses

### Reliability

- Deployed applications must have 99% uptime SLA
- Automated restarts on crashes must be configured
- Database connection pooling must handle at least 50 concurrent connections

## Dependencies *(optional)*

- **Frontend Code**: Requires `@specs/001-frontend-todo-ui/spec.md` to be implemented
- **Backend Code**: Requires `@specs/003-backend-task-crud/spec.md` and `@specs/002-authentication/spec.md` to be implemented
- **Database**: Requires Neon PostgreSQL account and project setup
- **Constitution**: Must comply with `@specs/000-constitution/spec.md` tech stack requirements (Next.js, FastAPI, Neon, Better Auth JWT)

## Assumptions *(optional)*

- User has git repository with frontend and backend code
- User has accounts on Vercel and Render/Fly.io platforms
- User has Neon PostgreSQL account
- Deployment platforms support environment variable configuration
- Neon provides PostgreSQL connection string in format `postgresql://user:password@host/database`

## Edge Cases *(optional)*

- **EC-001**: What happens if DATABASE_URL is invalid? → Backend fails to start with clear error message "Database connection failed"
- **EC-002**: What happens if BETTER_AUTH_SECRET is missing? → Backend fails to start with clear error message "BETTER_AUTH_SECRET environment variable is required"
- **EC-003**: What happens if deployment fails due to build error? → Platform displays build logs and deployment status as "Failed"
- **EC-004**: What happens if Neon database region has high latency? → Performance degrades but remains functional; consider region selection
- **EC-005**: What happens if backend and frontend are in different regions? → CORS must be configured to allow frontend origin

## Change Log *(mandatory)*

| Version | Date | Changes | Author |
|---------|--------|----------|---------|
| 1.0.0 | 2025-01-11 | Initial deployment setup specification for Vercel, Render/Fly.io, and Neon | Claude Code |
