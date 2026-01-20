// API Client with JWT handling
// Based on @specs/001-frontend-todo-ui/spec.md and @specs/002-authentication/spec.md

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// JWT Token Management
const JWT_KEY = 'jwt_token';

export const getJWT = (): string | null => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(JWT_KEY);
};

export const setJWT = (token: string): void => {
  if (typeof window === 'undefined') return;
  localStorage.setItem(JWT_KEY, token);
};

export const removeJWT = (): void => {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(JWT_KEY);
};

// Type definitions
export interface Task {
  id: number;
  user_id: string;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateTaskInput {
  title: string;
  description?: string;
}

export interface UpdateTaskInput {
  title: string;
  description?: string;
}

export interface ErrorResponse {
  detail: string;
}

// Helper function to add JWT token to headers
const getHeaders = (contentType = 'application/json'): HeadersInit => {
  const headers: HeadersInit = {};
  if (contentType) {
    headers['Content-Type'] = contentType;
  }

  const token = getJWT();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  return headers;
};

// Handle 401 responses
const handleResponse = async (response: Response) => {
  if (response.status === 401) {
    removeJWT();
    if (typeof window !== 'undefined') {
      window.location.href = '/signin';
    }
    throw new Error('Unauthorized. Please sign in again.');
  }

  if (!response.ok) {
    const error: ErrorResponse = await response.json();
    throw new Error(error.detail || 'Request failed');
  }

  return response.json();
};

// API Functions

/**
 * Get all tasks for a user
 * GET /api/{user_id}/tasks
 * Query params: status? (active/completed), sort_by? (created_at/title)
 */
export const getTasks = async (
  userId: string,
  options?: { status?: 'active' | 'completed'; sort_by?: 'created_at' | 'title' }
): Promise<Task[]> => {
  const params = new URLSearchParams();
  if (options?.status) params.append('status', options.status);
  if (options?.sort_by) params.append('sort_by', options.sort_by);

  const url = `${API_BASE_URL}/api/${userId}/tasks${params.toString() ? '?' + params.toString() : ''}`;

  const response = await fetch(url, {
    headers: getHeaders(),
  });

  return handleResponse(response);
};

/**
 * Get a single task
 * GET /api/{user_id}/tasks/{id}
 */
export const getTask = async (userId: string, taskId: number): Promise<Task> => {
  const url = `${API_BASE_URL}/api/${userId}/tasks/${taskId}`;

  const response = await fetch(url, {
    headers: getHeaders(),
  });

  return handleResponse(response);
};

/**
 * Create a new task
 * POST /api/{user_id}/tasks
 */
export const createTask = async (userId: string, taskData: CreateTaskInput): Promise<Task> => {
  const url = `${API_BASE_URL}/api/${userId}/tasks`;

  const response = await fetch(url, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(taskData),
  });

  return handleResponse(response);
};

/**
 * Update a task
 * PUT /api/{user_id}/tasks/{id}
 */
export const updateTask = async (
  userId: string,
  taskId: number,
  taskData: UpdateTaskInput
): Promise<Task> => {
  const url = `${API_BASE_URL}/api/${userId}/tasks/${taskId}`;

  const response = await fetch(url, {
    method: 'PUT',
    headers: getHeaders(),
    body: JSON.stringify(taskData),
  });

  return handleResponse(response);
};

/**
 * Delete a task
 * DELETE /api/{user_id}/tasks/{id}
 */
export const deleteTask = async (userId: string, taskId: number): Promise<void> => {
  const url = `${API_BASE_URL}/api/${userId}/tasks/${taskId}`;

  const response = await fetch(url, {
    method: 'DELETE',
    headers: getHeaders(),
  });

  if (response.status === 204) {
    return;
  }

  return handleResponse(response);
};

/**
 * Toggle task completion status
 * PATCH /api/{user_id}/tasks/{id}/complete
 */
export const toggleCompleteTask = async (userId: string, taskId: number): Promise<Task> => {
  const url = `${API_BASE_URL}/api/${userId}/tasks/${taskId}/complete`;

  const response = await fetch(url, {
    method: 'PATCH',
    headers: getHeaders(),
  });

  return handleResponse(response);
};

// Auth helper to extract user_id from JWT
export const getUserIdFromToken = (): string | null => {
  const token = getJWT();
  if (!token) return null;

  try {
    // Simple decode of JWT (without verification for client-side use)
    const payload = token.split('.')[1];
    const decoded = JSON.parse(atob(payload));
    return decoded.user_id || null;
  } catch {
    return null;
  }
};
