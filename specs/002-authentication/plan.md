# Implementation Plan: Authentication

**Branch**: `002-authentication` | **Date**: 2025-01-11 | **Spec**: @specs/002-authentication/spec.md
**Input**: Feature specification from `specs/002-authentication/spec.md`

## Summary

Implement Better Auth JWT integration for user authentication with signup, signin, and token verification middleware per constitution security requirements.

## Technical Context

**Language/Version**: Python (FastAPI) | **Framework**: FastAPI | **Auth**: Better Auth JWT |
**Primary Dependencies**: better-auth, python-jose[cryptography], python-multipart |
**Storage**: PostgreSQL via Neon (Better Auth managed users table) | **State Management**: JWT tokens (stateless) |
**Target Platform**: Server (API endpoints) | **Project Type**: REST API with JWT middleware |
**Performance Goals**: Token verification < 50ms | **Constraints**: BETTER_AUTH_SECRET must be shared |
**Scale/Scope**: 3 user stories (signup, signin, JWT verification), middleware implementation |

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Check against constitution**:
- [x] Spec references @specs/000-constitution/spec.md
- [x] Tech stack uses FastAPI for backend
- [x] Better Auth JWT integration specified
- [x] JWT token signing with BETTER_AUTH_SECRET
- [x] JWT verification middleware on all requests
- [x] 401 Unauthorized returns for invalid/expired tokens
- [x] user_id matching between JWT token and URL path
- [x] No alternative frameworks without justification

**Result**: ✅ PASS - All gates satisfied

## Project Structure

### Backend Code (target)

```text
backend/
├── main.py                      # FastAPI app with middleware
├── config.py                     # Better Auth configuration
├── models.py                      # User model (Better Auth)
├── middleware.py                  # JWT verification middleware
├── routes/
│   └── auth.py                  # Better Auth signup/signin routes (optional)
└── CLAUDE.md                     # Runtime guidance
```

### Key Decisions

1. **Better Auth Integration**
   - Use Better Auth library for user management
   - Better Auth provides built-in signup/signin handlers
   - Configure JWT plugin for token issuance

2. **JWT Token Format**
   - Sign using BETTER_AUTH_SECRET (HS256 algorithm)
   - Include user_id in token payload
   - Set expiration: 7 days (configurable)

3. **Middleware Implementation**
   - FastAPI dependency injection for JWT verification
   - Extract user_id from valid token
   - Attach user_id to request.state
   - Return 401 Unauthorized on invalid/expired tokens

4. **User Management**
   - Better Auth manages users table automatically
   - Email uniqueness check via Better Auth
   - Password hashing via Better Auth

## Architecture Overview

### Authentication Flow

```text
User (Browser)           Frontend             Better Auth           Backend API
    │                         │                      │                   │
    │ 1. Signup/Signin         │                      │                   │
    ├──────────────────────────>│                      │                   │
    │                         │                      │                   │
    │                         │ 2. Validate creds   │                   │
    │                         ├────────────────────>│                   │
    │                         │                      │                   │
    │                         │                      │ 3. Create user/ │
    │                         │                      │   Verify password │
    │                         │                      ├──────────────────>│
    │                         │                      │                   │
    │                         │                      │ 4. Issue JWT    │
    │                         │                      │   (signed with     │
    │                         │                      │    BETTER_AUTH_  │
    │                         │                      │    SECRET)         │
    │                         │                      ├──────────────────>│
    │                         │                      │                   │
    │                         │ 5. Receive token    │                   │
    │                         │<─────────────────────┤                   │
    │                         │                      │                   │
    │ 6. Store token          │                      │                   │
    │ (localStorage)            │                      │                   │
    │                         │                      │                   │
    │ 7. Make API request      │                      │                   │
    │ with token                │                      │                   │
    ├──────────────────────────>├──────────────────────┼──────────────────>│
    │                         │                      │                   │
    │ 8. Verify JWT           │                      │                   │
    │ (middleware)              │                      │                   │
    │<───────────────────────────────────────────────────┤                   │
    │                         │                      │                   │
    │ 9. Allow/Deny           │                      │                   │
    │<──────────────────────────┴──────────────────────┴──────────────────┘
```

### JWT Verification Middleware

```text
Request Arrives
    ↓
Extract Authorization header
    ↓
Token present?
    ├─ No → Return 401 Unauthorized
    └─ Yes → Decode JWT
        ↓
        Token valid?
        ├─ No → Return 401 Unauthorized ("Invalid/expired token")
        └─ Yes → Extract user_id
            ↓
            Attach user_id to request.state
            ↓
            Allow request to proceed
```

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Better Auth integration | Provides user management, JWT issuance, security best practices | Manual implementation would be error-prone and insecure |
| JWT middleware | Required per constitution for security on all requests | No middleware would require token check in every route manually |
