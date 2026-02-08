'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { getJWT, removeJWT, getUserIdFromToken, getTasks } from '@/lib/api';
import { TaskForm } from '@/components/TaskForm';
import { TaskItem } from '@/components/TaskItem';
import { ChatBot } from '@/components/ChatBot';
import type { Task } from '@/lib/api';

export default function TasksPage() {
  const router = useRouter();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState<'all' | 'active' | 'completed'>('all');
  const [sortBy, setSortBy] = useState<'created_at' | 'title'>('created_at');
  const [mounted, setMounted] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);

  // Handle mounting and authentication
  useEffect(() => {
    setMounted(true);
    const token = getJWT();
    const id = getUserIdFromToken();

    if (!token || !id) {
      router.push('/signin');
      return;
    }

    setUserId(id);
  }, [router]);

  // Load tasks when userId is available
  useEffect(() => {
    if (userId) {
      loadTasks();
    }
  }, [userId, filter, sortBy]);

  const loadTasks = async () => {
    if (!userId) return;

    setLoading(true);
    setError('');

    try {
      const data = await getTasks(userId, {
        status: filter === 'all' ? undefined : filter,
        sort_by: sortBy,
      });
      setTasks(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load tasks');
    } finally {
      setLoading(false);
    }
  };

  const handleSignout = () => {
    removeJWT();
    router.push('/signin');
  };

  // Show consistent loading state during SSR and initial mount
  if (!mounted || !userId) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 px-4 py-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-bold text-gray-900">My Tasks</h1>
            <p className="text-gray-600 mt-1">Organize and manage your work</p>
          </div>
          <button
            onClick={handleSignout}
            className="bg-red-600 text-white font-semibold py-2 px-6 rounded-lg hover:bg-red-700 transition shadow-md"
          >
            Sign Out
          </button>
        </div>

        {/* Stats Card */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          <div className="bg-white p-6 rounded-2xl shadow-md">
            <div className="text-3xl font-bold text-blue-600">{tasks.length}</div>
            <div className="text-gray-600 text-sm mt-1">Total Tasks</div>
          </div>
          <div className="bg-white p-6 rounded-2xl shadow-md">
            <div className="text-3xl font-bold text-green-600">{tasks.filter((t) => t.completed).length}</div>
            <div className="text-gray-600 text-sm mt-1">Completed</div>
          </div>
          <div className="bg-white p-6 rounded-2xl shadow-md">
            <div className="text-3xl font-bold text-orange-600">{tasks.filter((t) => !t.completed).length}</div>
            <div className="text-gray-600 text-sm mt-1">Active</div>
          </div>
        </div>

        {/* Task Form */}
        <TaskForm userId={userId} onTaskCreated={loadTasks} />

        {/* Filters */}
        <div className="bg-white p-5 rounded-2xl shadow-md mb-6 flex flex-wrap gap-4 items-center">
          <div className="flex items-center gap-3">
            <label htmlFor="filter" className="text-sm font-semibold text-gray-700">
              Filter:
            </label>
            <select
              id="filter"
              value={filter}
              onChange={(e) => {
                setFilter(e.target.value as 'all' | 'active' | 'completed');
              }}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition bg-gray-50 hover:bg-white"
            >
              <option value="all">All Tasks</option>
              <option value="active">Active</option>
              <option value="completed">Completed</option>
            </select>
          </div>

          <div className="flex items-center gap-3">
            <label htmlFor="sortBy" className="text-sm font-semibold text-gray-700">
              Sort by:
            </label>
            <select
              id="sortBy"
              value={sortBy}
              onChange={(e) => {
                setSortBy(e.target.value as 'created_at' | 'title');
              }}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition bg-gray-50 hover:bg-white"
            >
              <option value="created_at">Recently Added</option>
              <option value="title">Alphabetical</option>
            </select>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
            <svg className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <p className="text-red-700 text-sm font-medium">{error}</p>
          </div>
        )}

        {/* Tasks List */}
        <div className="bg-white p-8 rounded-2xl shadow-md">
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading tasks...</p>
            </div>
          ) : tasks.length === 0 ? (
            <div className="text-center py-12">
              <svg className="w-16 h-16 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              <p className="text-gray-500 text-lg">No tasks yet</p>
              <p className="text-gray-400 text-sm mt-1">Add your first task above!</p>
            </div>
          ) : (
            <ul className="space-y-3">
              {tasks.map((task) => (
                <TaskItem
                  key={task.id}
                  task={task}
                  userId={userId}
                  onTaskUpdated={loadTasks}
                />
              ))}
            </ul>
          )}
        </div>

        {/* ChatBot */}
        <ChatBot userId={userId} onTaskUpdate={loadTasks} />
      </div>
    </div>
  );
}
