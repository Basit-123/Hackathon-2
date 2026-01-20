# Constitution Runtime Guidance

**Purpose**: Guidelines for following project constitution during all development phases

## Constitution Overview

The Hackathon II Phase 2 Todo application constitution defines 6 core principles that ALL team members must follow:

1. **Spec-Driven Development (NON-NEGOTIABLE)**
   - All feature work starts with `/sp.specify` to create/update specs
   - All plans are generated via `/sp.plan` based on existing specs
   - All task breakdowns happen via `/sp.tasks`
   - All implementation happens via `/sp.implement` using Claude Code agents
   - Reference specs using `@specs/NNN-feature-name/spec.md` syntax

2. **Monorepo Structure**
   - All code lives in `frontend/` or `backend/` directories
   - All specs live in `specs/NNN-feature-name/` folders
   - Each package has its own `CLAUDE.md` with runtime guidance
   - Cross-package dependencies must be explicitly declared

3. **Multi-User Security Isolation**
   - Backend filters ALL queries by `user_id` from JWT token
   - API endpoints use `/api/{user_id}/tasks` pattern
   - `user_id` in URL must match `user_id` from JWT token
   - Mismatch returns 401 Unauthorized immediately

4. **JWT Authentication Flow**
   - Better Auth handles signup/signin and JWT issuance
   - Frontend stores JWT and includes `Authorization: Bearer <token>` header
   - Backend implements JWT verification middleware
   - Shared `BETTER_AUTH_SECRET` used across frontend/backend

5. **Tech Stack Adherence**
   - Frontend: Next.js 16+ App Router, TypeScript, Tailwind CSS
   - Backend: FastAPI, SQLModel, Neon PostgreSQL
   - Auth: Better Auth with JWT plugin
   - Deviations require ADR documentation and team approval

6. **Independent User Story Delivery**
   - Features broken into P1, P2, P3 priority stories
   - Each story independently testable and deployable
   - Tasks organized by user story in `tasks.md`

## Workflow Commands

### Spec-Kit Plus Workflow

```bash
# For any new feature or update:
/sp.specify <feature-name>     # Create/update specification
/sp.clarify <feature-name>   # Clarify ambiguities (optional)
/sp.plan <feature-name>        # Generate implementation plan
/sp.tasks <feature-name>       # Break into atomic tasks
/sp.implement <feature-name>    # Execute tasks via agents
```

### Constitution Reference

When working on ANY feature or task, consult the constitution:
- Read `.specify/memory/constitution.md` for full governance
- Reference specific principles using `@specs/000-constitution/spec.md`
- Verify compliance before proceeding to next phase

## Quick Reference

### Security Checklist

Before deploying ANY backend code:
- [ ] JWT verification middleware in place
- [ ] All routes check `user_id` from JWT matches URL
- [ ] 401 Unauthorized returned on invalid token
- [ ] All database queries filter by `user_id`

### Tech Stack Validation

Before starting implementation:
- [ ] Frontend uses Next.js 16+ App Router
- [ ] Backend uses FastAPI
- [ ] Database uses SQLModel with Neon PostgreSQL
- [ ] Auth uses Better Auth with JWT

### Workflow Validation

Before proceeding to next phase:
- [ ] spec.md exists and is complete
- [ ] plan.md exists and passes constitution check
- [ ] tasks.md exists with atomic tasks organized by story
