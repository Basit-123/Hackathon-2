# Frontend Todo UI Requirements

**Purpose**: High-level requirements for Next.js 16+ Task List UI with JWT integration

## What We Need

The frontend needs to provide a modern, responsive user interface for managing tasks with:

1. **Task Display**
   - List tasks with filtering (active/completed status)
   - Sorting options (by creation date or title)
   - Responsive design for mobile and desktop

2. **Task Creation**
   - Form to add new tasks with title and optional description
   - Client-side validation for required fields

3. **Task Actions**
   - Edit existing tasks (title, description)
   - Delete tasks
   - Toggle completion status
   - All actions require JWT authentication

4. **Authentication UI**
   - Signup page (user creation)
   - Signin page (JWT token retrieval)
   - Protected routes redirect to signin if not authenticated

5. **API Integration**
   - Client for making API requests with JWT Bearer token
   - Handle 401 Unauthorized responses
   - Secure token storage

## Success Criteria

- Users can view all their tasks with filtering and sorting
- Users can create, edit, delete, and complete tasks
- Authentication works and JWT tokens are stored correctly
- UI is responsive on mobile and desktop
