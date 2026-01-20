# Authentication Requirements

**Purpose**: High-level requirements for Better Auth JWT integration for Todo application

## What We Need

The application needs secure user authentication with:

1. **User Registration**
   - Users can create accounts with email and password
   - Better Auth manages user table and sessions

2. **User Signin**
   - Users can signin with email and password
   - Better Auth issues JWT token on successful signin

3. **JWT Token Management**
   - Token contains user_id
   - Token is signed with shared BETTER_AUTH_SECRET
   - Token has expiration time

4. **Token Verification**
   - Backend validates all requests using JWT token
   - Middleware extracts user_id from token
   - Returns 401 on invalid/expired tokens

## Success Criteria

- Users can signup and create accounts
- Users can signin and receive JWT token
- Backend verifies JWT on all API requests
- Invalid tokens return 401 Unauthorized
