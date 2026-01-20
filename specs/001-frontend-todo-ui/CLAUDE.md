# Frontend Todo UI Runtime Guidance

**Purpose**: Development guidelines for Next.js 16+ Task List UI implementation

## Tech Stack (from @specs/000-constitution/spec.md)

- **Framework**: Next.js 16+ App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Authentication**: Better Auth with JWT

## Component Patterns

### Server Components (Default)

Use Server Components for:
- Initial data fetching (tasks list page)
- SEO-critical pages (landing, signin, signup)
- Components that don't need interactivity

```typescript
// app/tasks/page.tsx - Server Component
import { getTasks } from "@/lib/api"

export default async function TasksPage() {
  const tasks = await getTasks()
  return <TaskList tasks={tasks} />
}
```

### Client Components

Use Client Components (add `'use client'` at top) for:
- Forms with event handlers (TaskForm)
- Buttons with onClick handlers (complete, delete, edit)
- Stateful components (filter controls, sort options)

```typescript
'use client'

export function TaskForm({ onSubmit }) {
  const [title, setTitle] = useState('')
  return <input onChange={e => setTitle(e.target.value)} />
}
```

## API Client Usage

### Import from @/lib/api

```typescript
import { getTasks, createTask, updateTask, deleteTask } from '@/lib/api'
```

### JWT Token Handling

API client automatically includes JWT token from localStorage:
- Token is stored on successful signin/signup
- Token is included in `Authorization: Bearer <token>` header
- 401 responses trigger redirect to signin page

### Example Usage

```typescript
// Fetch tasks with filtering
const tasks = await getTasks({ status: 'active', sort_by: 'created_at' })

// Create new task
await createTask({ title: 'Buy groceries', description: 'Get milk' })

// Toggle task completion
await toggleCompleteTask(taskId)
```

## Better Auth Integration

### Server Actions

Better Auth provides server actions in `frontend/app/api/auth/`:
- Server actions handle signup/signin logic
- Automatically issue JWT tokens on success
- Frontend redirects based on response

### Pages

- `app/signup/page.tsx` - Better Auth signup form
- `app/signin/page.tsx` - Better Auth signin form
- Forms use Better Auth UI components

## Responsive Design

### Mobile-First Approach

Use Tailwind mobile classes first, then expand:

```typescript
// Mobile: flex-col (stacked)
// md+: flex-row (side-by-side)
<div className="flex flex-col md:flex-row gap-4">
  <div className="flex-1">...</div>
  <div className="flex-1">...</div>
</div>
```

### Breakpoints

- `sm`: 640px and up
- `md`: 768px and up
- `lg`: 1024px and up
- `xl`: 1280px and up

### Common Patterns

```typescript
// Responsive grid
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">

// Responsive text
<h1 className="text-2xl md:text-4xl">Tasks</h1>

// Responsive padding
<div className="p-4 md:p-8">
```

## State Management

### Local State (useState/useEffect)

For simple forms and components:

```typescript
const [tasks, setTasks] = useState<Task[]>([])
const [filter, setFilter] = useState<'all' | 'active' | 'completed'>('all')

useEffect(() => {
  loadTasks()
}, [filter])
```

### No Complex State Needed

This application doesn't need:
- Redux/Zustand (simple local state is sufficient)
- React Query (optional optimization, not required for MVP)

## Error Handling

### API Errors

```typescript
try {
  await createTask(taskData)
} catch (error) {
  if (error.status === 401) {
    router.push('/signin')  // Redirect to signin
  } else {
    alert('Failed to create task')
  }
}
```

### Validation Errors

Display inline validation messages:

```typescript
<div className="text-red-500">
  {errors.title && 'Title is required'}
</div>
```

## Development Workflow

1. **Start with Server Component**: Create page that fetches data
2. **Add Client Components**: Break down into interactive components
3. **Use API Client**: All data operations via `lib/api.ts`
4. **Test Responsiveness**: Check mobile, tablet, desktop viewports
5. **Verify Auth Flow**: Test signin, protected routes, JWT handling

## Common Pitfalls

**Avoid**:
- Using Client Components when Server Component would work
- Fetching data inside Client Components (use Server Components for initial load)
- Storing JWT in URL parameters or localStorage without XSS protection
- Hardcoding API URLs (use `NEXT_PUBLIC_API_URL` environment variable)

**Use Instead**:
- Server Components for initial data fetch
- Client Components only for interactivity
- Secure localStorage for JWT (httpOnly cookies for future enhancement)
- Environment variables for all configuration
