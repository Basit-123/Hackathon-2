'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { getJWT, removeJWT, getUserIdFromToken, getTasks } from '@/lib/api';
import { TaskForm } from '@/components/TaskForm';
import { TaskItem } from '@/components/TaskItem';
import type { Task } from '@/lib/api';

export default function TasksPage() {
  const router = useRouter();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState<'all' | 'active' | 'completed'>('all');
  const [sortBy, setSortBy] = useState<'created_at' | 'title'>('created_at');

  const userId = getUserIdFromToken();

  useEffect(() => {
    const token = getJWT();
    if (!token || !userId) {
      router.push('/signin');
      return;
    }

    loadTasks();
  }, [userId, router]);

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

  if (!userId) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 px-4 py-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">My Tasks</h1>
          <button
            onClick={handleSignout}
            className="bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500"
          >
            Sign Out
          </button>
        </div>

        {/* Filters */}
        <div className="bg-white p-4 rounded-lg shadow-md mb-6">
          <div className="flex flex-wrap gap-4 items-center">
            <div className="flex items-center gap-2">
              <label htmlFor="filter" className="text-sm font-medium text-gray-700">
                Filter:
              </label>
              <select
                id="filter"
                value={filter}
                onChange={(e) => {
                  setFilter(e.target.value as any);
                }}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All</option>
                <option value="active">Active</option>
                <option value="completed">Completed</option>
              </select>
            </div>

            <div className="flex items-center gap-2">
              <label htmlFor="sortBy" className="text-sm font-medium text-gray-700">
                Sort by:
              </label>
              <select
                id="sortBy"
                value={sortBy}
                onChange={(e) => {
                  setSortBy(e.target.value as any);
                }}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="created_at">Date Created</option>
                <option value="title">Title</option>
              </select>
            </div>
          </div>
        </div>

        {/* Task Form */}
        <TaskForm userId={userId} onTaskCreated={loadTasks} />

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        {/* Tasks List */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-bold mb-4">Your Tasks</h2>

          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading tasks...</p>
            </div>
          ) : tasks.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-600 mb-4">
                {filter === 'all'
                  ? "You don't have any tasks yet. Create your first task!"
                  : `No ${filter} tasks found.`}
              </p>
              {filter !== 'all' && (
                <button
                  onClick={() => setFilter('all')}
                  className="text-blue-600 hover:underline"
                >
                  Show all tasks
                </button>
              )}
            </div>
          ) : (
            <div className="space-y-3">
              {tasks.map((task) => (
                <TaskItem
                  key={task.id}
                  task={task}
                  userId={userId}
                  onTaskUpdated={loadTasks}
                />
              ))}
            </div>
          )}
        </div>

        {/* Stats */}
        <div className="mt-6 text-center text-sm text-gray-600">
          Total tasks: {tasks.length}
          {tasks.some((t) => !t.completed) && (
            <span className="ml-4">
              Active: {tasks.filter((t) => !t.completed).length}
            </span>
          )}
          {tasks.some((t) => t.completed) && (
            <span className="ml-4">
              Completed: {tasks.filter((t) => t.completed).length}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
