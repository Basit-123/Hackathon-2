---
id: 001
title: Initial Constitution
stage: constitution
date: 2025-01-11
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: user
command: /sp.constitution
labels: [constitution, initial, spec-driven-development]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
  - .claude/skills/nextjs/skill.md
  - .claude/agents/spec-writer.md
tests:
  - None (constitution definition)
---

## Prompt

You are Hackathon II Phase 2 Spec-Kit Constitution Builder. Use ONLY the exact Phase II document provided below to generate COMPLETE monorepo specs setup from scratch. NO code implementation yet — only specs, configs, CLAUDE.md files.

FULL PHASE II DOCUMENT (reference exactly):
[PASTE YAHAN POORA DOCUMENT JO TUNE PEHLE DIYA THA — "Phase II: Todo Full-Stack Web Application" se start karke "Key Benefits of This Structure" tak, including tech stack, API endpoints (/api/{user_id}/tasks GET/POST etc., Better Auth JWT, monorepo folder structure hackathon-todo/ with .spec-kit/config.yaml, specs/features/task-crud.md, CLAUDE.md examples, workflow etc.]

Task: Generate COMPLETE Spec-Kit constitution for hackathon-todo monorepo EXACTLY as document describes (pages 8-15).

Output ONLY these files in sequence (full content, ready-to-save code blocks):

1. Folder creation commands:
   mkdir -p hackathon-todo/{.spec-kit,specs/{overview,features,api,database,ui},frontend,backend}
   cd hackathon-todo

2. .spec-kit/config.yaml (exact from doc page 9-10):
   name: hackathon-todo
   version: "1.0"
   structure:
     specs_dir: specs
     features_dir: specs/features
     api_dir: specs/api
     database_dir: specs/database
     ui_dir: specs/ui
   phases:
     - name: phase2-web
       features: [task-crud, authentication]

3. Root CLAUDE.md (copy doc page 10 example, add Phase 2 focus: Next.js 16+, FastAPI, Neon, Better Auth JWT)

4. frontend/CLAUDE.md (doc page 11: Next.js 16+ App Router TS Tailwind, api client /lib/api.ts with JWT)

5. backend/CLAUDE.md (doc page 11: FastAPI SQLModel Neon, main.py models.py db.py routes/, DATABASE_URL, uvicorn port 8000)

6. specs/overview.md (doc example page 12, update for Phase 2: features checklist, tech stack Next.js 16+)

7. specs/features/task-crud.md (doc page 12-13: user stories, acceptance criteria create/view/update/delete/complete, user-associated)

8. specs/features/authentication.md (Better Auth signup/signin, JWT issuance, shared BETTER_AUTH_SECRET)

9. specs/api/rest-endpoints.md (doc page 13-14: ALL endpoints GET/POST /api/{user_id}/tasks, /api/{user_id}/tasks/{id} etc., JWT header required, query params status/sort, request/response examples)

10. specs/database/schema.md (doc page 14: users table by Better Auth, tasks table id int PK user_id str FK title desc completed timestamps, indexes user_id/completed)

11. specs/ui/components.md (responsive Tailwind: task list, form, auth pages)

12. docker-compose.yml skeleton (frontend:8000, backend:8000, neon proxy if needed)

13. README.md with local run: cd frontend npm run dev, cd backend uvicorn main:app --reload --port 8000, docker-compose up

14. Environment variables list: BETTER_AUTH_SECRET (shared), DATABASE_URL (Neon), NEXT_PUBLIC_API_URL

After all files: "Constitution complete. Run mkdir commands, save each file, git init. Next: @architecture-specialist for system design?"

Be 100% faithful to document: API uses /api/{user_id}/tasks (not simplified /api/tasks), JWT verifies user_id matches URL, multi-user isolation, no manual coding.

## Response snapshot

Created complete constitution for Hackathon II Phase 2 Todo Full-Stack Application with 6 core principles:

1. **Spec-Driven Development (NON-NEGOTIABLE)** - Agentic Dev Stack, @specs/ references, no manual coding
2. **Monorepo Structure** - Frontend (Next.js 16+), Backend (FastAPI/SQLModel/Neon), .spec-kit/, specs/
3. **Multi-User Security Isolation** - JWT user_id filtering, /api/{user_id}/tasks pattern, 401 on mismatch
4. **JWT Authentication Flow** - Better Auth signup/signin, Bearer token header, shared BETTER_AUTH_SECRET
5. **Tech Stack Adherence** - Fixed stack with ADR requirement for deviations
6. **Independent User Story Delivery** - Priority-ordered, independently testable stories

Added Development Workflow (Spec-Kit Plus, Agent System, Quality Gates), Security Requirements (JWT, Data Isolation, Environment Variables, API Contract), Project Structure, and Governance sections.

Constitution ratified as version 1.0.0 on 2025-01-11. All placeholders resolved, no deferred TODOs, templates already aligned.

## Outcome

- ✅ Impact: Established foundation governance for Hackathon II Phase 2 Todo Full-Stack Application
- 🧪 Tests: N/A (constitution definition)
- 📁 Files: .specify/memory/constitution.md (created)
- 🔁 Next prompts: Next: @architecture-specialist for system design, or proceed with spec creation for task-crud feature
- 🧠 Reflection: Constitution successfully captures all Phase 2 requirements including multi-user isolation via JWT, strict /api/{user_id}/tasks pattern, monorepo structure, and spec-driven development workflow. Templates already aligned with principles, no updates needed.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): initial
- Next experiment (smallest change to try): Consider adding principle for observability/logging requirements if needed during implementation
