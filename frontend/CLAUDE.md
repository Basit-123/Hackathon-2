# Frontend Runtime Guidance

**Purpose**: Development guidelines for Next.js 16+ Task List UI implementation

## Tech Stack (from @specs/000-constitution/spec.md)

- **Framework**: Next.js 16+ App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Authentication**: JWT token-based (localStorage)
- **API Client**: Custom implementation in `lib/api.ts`

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx                # Root layout with fonts and metadata
│   ├── page.tsx                  # Landing page (redirects to signin/tasks)
│   ├── signin/
│   │   └── page.tsx              # Signin page
│   ├── signup/
│   │   └── page.tsx              # Signup page
│   └── tasks/
│       └── page.tsx              # Tasks list page
├── components/
│   ├── TaskForm.tsx              # Create task form component
│   └── TaskItem.tsx              # Single task display component
├── lib/
│   └── api.ts                   # Centralized API client
├── middleware.ts                # Route protection middleware
└── CLAUDE.md                    # This file
```

## Component Patterns

### Client Components (use `'use client'`)

Use Client Components for:
- Forms with event handlers (TaskForm, TaskItem edit form)
- Buttons with onClick handlers (complete, delete, edit)
- Stateful components (filter controls, sort options, loading states)

**When to add `'use client'`**: Add as the first line of the file

```typescript
'use client';

import { useState } from 'react';

export function TaskForm({ userId, onTaskCreated }: TaskFormProps) {
  const [title, setTitle] = useState('');
  // ... rest of component
}
```

### Server Components (default)

Use Server Components for:
- Initial page load (tasks page is client component in this implementation)
- Data fetching (if we were using server-side rendering)
- SEO-critical pages (landing page is a simple redirect)

**Note**: Tasks page uses client component because it requires state for filters and user authentication check

## API Client Usage

### Import from @/lib/api

```typescript
import {
  getTasks,
  createTask,
  updateTask,
  deleteTask,
  toggleCompleteTask,
  getJWT,
  setJWT,
  removeJWT,
  getUserIdFromToken
} from '@/lib/api';
```

### JWT Token Management

```typescript
// Get current JWT token
const token = getJWT();

// Set JWT token after signin
setJWT(token);

// Remove JWT token on signout
removeJWT();

// Extract user_id from JWT
const userId = getUserIdFromToken();
```

### API Functions

```typescript
// Get tasks with filtering and sorting
const tasks = await getTasks(userId, {
  status: 'active',      // optional: 'all' | 'active' | 'completed'
  sort_by: 'created_at'  // optional: 'created_at' | 'title'
});

// Create new task
await createTask(userId, {
  title: 'Buy groceries',
  description: 'Get milk and eggs'
});

// Update task
await updateTask(userId, taskId, {
  title: 'Updated title',
  description: 'Updated description'
});

// Delete task
await deleteTask(userId, taskId);

// Toggle task completion
await toggleCompleteTask(userId, taskId);
```

### Error Handling

All API functions throw errors on failure. Use try-catch:

```typescript
try {
  await createTask(userId, taskData);
  // Success - handle success
  onTaskCreated();
} catch (err) {
  // Error - handle error
  setError(err instanceof Error ? err.message : 'Failed to create task');
}
```

### 401 Unauthorized Handling

The API client automatically handles 401 errors:
- JWT token is removed from localStorage
- User is redirected to `/signin` page

## Authentication Flow

### Signin Flow

1. User navigates to `/signin`
2. User enters email and password
3. Form submits to backend API (`/auth/signin`)
4. Backend validates credentials and returns JWT token
5. Frontend stores token using `setJWT(token)`
6. User is redirected to `/tasks`

### Signup Flow

1. User navigates to `/signup`
2. User enters email, password, and confirm password
3. Frontend validates passwords match
4. Form submits to backend API (`/auth/signup`)
5. Backend creates account
6. User is redirected to `/signin` to sign in

### Signout Flow

```typescript
import { removeJWT } from '@/lib/api';
import { useRouter } from 'next/navigation';

const router = useRouter();
removeJWT();
router.push('/signin');
```

## Route Protection

### Middleware

The `middleware.ts` file protects routes:
- Public paths: `/signin`, `/signup`
- Protected paths: `/tasks`, `/` (redirects based on auth state)

### Client-Side Protection

Protected pages (like `/tasks`) should check for JWT token:

```typescript
useEffect(() => {
  const token = getJWT();
  const userId = getUserIdFromToken();

  if (!token || !userId) {
    router.push('/signin');
  }
}, [router]);
```

## Responsive Design

### Mobile-First Approach

Tailwind classes are organized from mobile to desktop:

```typescript
// Mobile: single column (flex-col)
// md+: two columns (flex-row)
<div className="flex flex-col md:flex-row gap-4">
  <div className="flex-1">...</div>
  <div className="flex-1">...</div>
</div>
```

### Breakpoints

- `sm`: 640px and up (small phones to tablets)
- `md`: 768px and up (tablets)
- `lg`: 1024px and up (laptops)
- `xl`: 1280px and up (large screens)

### Common Responsive Patterns

```typescript
// Responsive container
<div className="max-w-4xl mx-auto px-4 py-8">

// Responsive grid
<div className="grid grid-cols-1 md:grid-cols-2 gap-4">

// Responsive text
<h1 className="text-3xl md:text-4xl">Tasks</h1>

// Responsive padding
<div className="p-4 md:p-6">

// Responsive flex
<div className="flex flex-col md:flex-row items-start justify-between">
```

## State Management

### Local State (useState/useEffect)

Simple local state is sufficient for this app:

```typescript
const [tasks, setTasks] = useState<Task[]>([]);
const [filter, setFilter] = useState<'all' | 'active' | 'completed'>('all');
const [sortBy, setSortBy] = useState<'created_at' | 'title'>('created_at');
const [loading, setLoading] = useState(false);
const [error, setError] = useState('');
```

### No Global State Needed

This application doesn't need:
- Redux/Zustand (simple local state is sufficient)
- React Query (optional optimization, not required for MVP)
- Context API (component props work fine)

## Form Handling

### Task Form Pattern

```typescript
const [title, setTitle] = useState('');
const [description, setDescription] = useState('');

const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();

  if (!title.trim()) {
    setError('Title is required');
    return;
  }

  try {
    await createTask(userId, { title, description });
    setTitle('');
    setDescription('');
    onTaskCreated();
  } catch (err) {
    setError(err.message);
  }
};
```

### Form Validation

- Title: Required, must not be empty after trimming
- Description: Optional
- Password (signup): Minimum 6 characters
- Password (signup): Must match confirmation password

## Styling Guidelines

### Colors

- Primary: `bg-blue-600` for main actions
- Success: `bg-green-100 text-green-700` for completed tasks
- Error: `bg-red-50 border-red-200 text-red-600` for error messages
- Background: `bg-gray-100` for page background
- Card: `bg-white` with shadow for containers

### Buttons

```typescript
// Primary button
<button className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700">

// Secondary button
<button className="bg-gray-200 text-gray-700 py-1 px-3 rounded hover:bg-gray-300">

// Destructive button
<button className="bg-red-100 text-red-700 py-1 px-3 rounded hover:bg-red-200">

// Disabled state
<button disabled className="opacity-50 cursor-not-allowed">
```

### Inputs

```typescript
<input className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
```

## Development Workflow

1. **Start with page structure**: Create the page file (e.g., `app/tasks/page.tsx`)
2. **Add client components**: Break down into reusable components (TaskForm, TaskItem)
3. **Use API client**: All data operations via `lib/api.ts`
4. **Handle authentication**: Check JWT token on protected routes
5. **Test responsiveness**: Check mobile (375px), tablet (768px), desktop (1024px+)
6. **Verify auth flow**: Test signin, protected routes, JWT handling

## Environment Variables

Create `.env.local` in `frontend/`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Note: `NEXT_PUBLIC_` prefix makes the variable available in browser code.

## Running the App

```bash
cd frontend
npm run dev
```

App runs on `http://localhost:3000`

## Common Pitfalls

**Avoid**:
- Using Server Components when interactivity is needed
- Fetching data inside Client Components without useEffect
- Storing JWT in URL parameters or without XSS protection
- Hardcoding API URLs (use `NEXT_PUBLIC_API_URL`)

**Use Instead**:
- Client Components only when needed (forms, buttons with handlers)
- Fetch data with proper error handling and loading states
- localStorage for JWT (httpOnly cookies for future enhancement)
- Environment variables for all configuration

## Testing Checklist

Before deploying, verify:
- [ ] User can signup with valid email and password
- [ ] User can signin with correct credentials
- [ ] Invalid credentials show error message
- [ ] Protected routes redirect to signin without JWT
- [ ] User can create a task
- [ ] User can view all their tasks
- [ ] User can filter tasks by status
- [ ] User can sort tasks by date or title
- [ ] User can edit task title and description
- [ ] User can delete task with confirmation
- [ ] User can toggle task completion
- [ ] Completed tasks show visual feedback (strikethrough, opacity)
- [ ] Empty state displays correctly
- [ ] Signout works and redirects to signin
- [ ] 401 errors redirect to signin
- [ ] Layout is responsive on mobile, tablet, and desktop
