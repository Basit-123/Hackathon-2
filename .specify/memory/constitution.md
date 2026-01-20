<!--
  SYNC IMPACT REPORT
  ===================
  Version Change: (none) → 1.0.0 (initial ratification)

  Modified Principles: (none - initial creation)

  Added Sections:
    - Core Principles: 6 new principles
    - Development Workflow
    - Security Requirements
    - Governance

  Removed Sections: (none)

  Templates Requiring Updates:
    ✅ plan-template.md - Already contains Constitution Check section
    ✅ spec-template.md - Already aligns with principle-driven requirements
    ✅ tasks-template.md - Already supports task categorization by story
    ⚠ commands/ - No command files found (none need updates)

  Follow-up TODOs: (none)

-->
# Hackathon Todo Constitution

## Core Principles

### I. Spec-Driven Development (NON-NEGOTIABLE)

All feature work MUST follow the Agentic Dev Stack: 1) Update/Read specs first, 2) Generate plan, 3) Break into atomic tasks, 4) Implement via Claude Code (no manual coding). Implementation work must reference existing specifications using `@specs/path/to/file.md` syntax. Specs live under `specs/` directory (overview, features/, api/, database/, ui/) and serve as the single source of truth for requirements, API contracts, and data models.

**Rationale**: Prevents scope creep, ensures all changes are traceable to requirements, and enables automated consistency checks between specs, plans, and implementation.

### II. Monorepo Structure

The project uses a strict monorepo layout: `hackathon-todo/` with `frontend/` (Next.js 16+ App Router TS Tailwind), `backend/` (FastAPI SQLModel Neon), `.spec-kit/` (configuration), and `specs/` (all specifications). Cross-package dependencies MUST be declared explicitly. Each package has its own `CLAUDE.md` with runtime guidance.

**Rationale**: Coordinated versioning, shared tooling, clear separation of concerns while maintaining project cohesion.

### III. Multi-User Security Isolation

All data access MUST enforce strict user isolation. Backend MUST filter ALL queries by `user_id` extracted from JWT token. API endpoints MUST use `/api/{user_id}/tasks` pattern where the `user_id` in URL must match the `user_id` from JWT token. Any mismatch returns 401 Unauthorized. Better Auth handles user management; tasks table includes `user_id` FK to users table.

**Rationale**: Prevents cross-user data leakage, ensures security by default, enforces least privilege access.

### IV. JWT Authentication Flow

Better Auth handles signup/signin and JWT token issuance. Frontend stores JWT in secure storage and includes `Authorization: Bearer <token>` header on ALL API requests. Backend implements JWT verification middleware that validates token, extracts `user_id`, and makes it available to route handlers. Shared secret `BETTER_AUTH_SECRET` used across frontend/backend.

**Rationale**: Stateless authentication, scalable architecture, standard security practice, decoupled auth from business logic.

### V. Tech Stack Adherence

Technology choices are fixed: Next.js 16+ App Router with TypeScript and Tailwind CSS for frontend; FastAPI with SQLModel for backend; Neon PostgreSQL for database; Better Auth with JWT for authentication. Deviations MUST be documented with ADR and approved. No alternative frameworks without justification.

**Rationale**: Reduces decision fatigue, ensures team familiarity, leverages established patterns, maintains consistency.

### VI. Independent User Story Delivery

Features MUST be broken into independently testable and deliverable user stories. Each story must provide complete value when implemented alone. Stories should follow priority order (P1, P2, P3) and be deployable independently. Tasks are organized by user story in `tasks.md` to enable parallel development.

**Rationale**: Enables incremental value delivery, supports parallel development, allows early feedback, reduces integration risk.

## Development Workflow

### Spec-Kit Plus Workflow

1. **Specify**: Create or update feature specs in `specs/features/[feature-name].md` with user stories, acceptance criteria, and requirements.
2. **Plan**: Run `/sp.plan` to generate architecture plan, research, data model, and contracts.
3. **Tasks**: Run `/sp.tasks` to break plan into atomic implementation tasks organized by user story.
4. **Implement**: Execute tasks via Claude Code agents (backend-specialist, frontend-specialist, deployment-expert).
5. **Test**: Validate each user story independently before proceeding.
6. **Deploy**: Incrementally deploy using monorepo strategy.

### Agent System

- **main session**: Orchestration, coordination, guidance
- **architecture-specialist**: System design, ADR creation, validation of multi-user isolation
- **frontend-specialist**: Next.js UI, Better Auth pages, API client with JWT
- **backend-specialist**: FastAPI routes, JWT middleware, SQLModel models
- **deployment-expert**: Vercel/Render deployment, environment variables, Neon DB setup
- **spec-writer**: ONLY writes specs, never code

### Quality Gates

- Every spec MUST have testable acceptance criteria
- Every plan MUST pass Constitution Check
- Every task set MUST be organized by user story
- Every PR must validate user story independence
- Every deployment must verify multi-user isolation

## Security Requirements

### JWT Token Handling

- Tokens MUST be validated on EVERY backend request
- Token MUST be sent via `Authorization: Bearer <token>` header
- Backend MUST return 401 Unauthorized for invalid/expired tokens
- Token extraction and `user_id` matching MUST happen before any data access

### Data Isolation

- ALL queries MUST filter by `user_id` from JWT token
- `user_id` in URL path `/api/{user_id}/tasks` MUST match JWT token's `user_id`
- No direct database access from frontend
- No sharing of data between users under any circumstances

### Environment Variables

- `BETTER_AUTH_SECRET`: Shared secret for JWT signing/validation
- `DATABASE_URL`: Neon PostgreSQL connection string
- `NEXT_PUBLIC_API_URL`: Backend API URL for frontend
- Secrets MUST never be committed to repository

### API Contract

- Endpoints: GET/POST `/api/{user_id}/tasks`, GET/PUT/DELETE `/api/{user_id}/tasks/{id}`, PATCH `/api/{user_id}/tasks/{id}/complete`
- Query params: `status` (active/completed), `sort_by` (created_at/title)
- Request/Response formats must match `specs/api/rest-endpoints.md`
- All error responses include appropriate HTTP status codes

## Project Structure

```
hackathon-todo/
├── .spec-kit/
│   └── config.yaml
├── specs/
│   ├── overview.md
│   ├── features/
│   │   ├── task-crud.md
│   │   └── authentication.md
│   ├── api/
│   │   └── rest-endpoints.md
│   ├── database/
│   │   └── schema.md
│   └── ui/
│       └── components.md
├── frontend/
│   ├── CLAUDE.md
│   ├── app/
│   ├── lib/
│   │   └── api.ts
│   └── package.json
├── backend/
│   ├── CLAUDE.md
│   ├── main.py
│   ├── models.py
│   ├── db.py
│   └── routes/
├── docker-compose.yml
└── README.md
```

## Governance

### Amendment Procedure

Constitution changes require:
1. Documented rationale and impact analysis
2. ADR creation for architectural changes
3. Team approval via pull request review
4. Migration plan for any breaking changes
5. Version increment following semantic versioning:
   - MAJOR: Backward incompatible principle removals or redefinitions
   - MINOR: New principle or materially expanded guidance
   - PATCH: Clarifications, wording, non-semantic refinements

### Compliance Review

All pull requests and feature work must:
- Verify compliance with all core principles
- Check specs exist and are referenced
- Validate multi-user isolation requirements
- Ensure task organization by user story
- Confirm tech stack adherence

### Runtime Guidance

Use `CLAUDE.md` files for implementation-specific guidance:
- Root: Project-level guidance and workflow
- `frontend/CLAUDE.md`: Next.js patterns, API client usage
- `backend/CLAUDE.md`: FastAPI patterns, JWT middleware, SQLModel usage

**Version**: 1.0.0 | **Ratified**: 2025-01-11 | **Last Amended**: 2025-01-11
