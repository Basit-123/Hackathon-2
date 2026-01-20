'use client';

import { useState } from 'react';
import { updateTask, deleteTask, toggleCompleteTask } from '@/lib/api';
import type { Task } from '@/lib/api';

interface TaskItemProps {
  task: Task;
  userId: string;
  onTaskUpdated: () => void;
}

export function TaskItem({ task, userId, onTaskUpdated }: TaskItemProps) {
  const [editing, setEditing] = useState(false);
  const [title, setTitle] = useState(task.title);
  const [description, setDescription] = useState(task.description || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this task?')) {
      return;
    }

    setLoading(true);
    try {
      await deleteTask(userId, task.id);
      onTaskUpdated();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete task');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleComplete = async () => {
    setLoading(true);
    try {
      await toggleCompleteTask(userId, task.id);
      onTaskUpdated();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update task');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!title.trim()) {
      setError('Title is required');
      return;
    }

    setLoading(true);
    try {
      await updateTask(userId, task.id, {
        title: title.trim(),
        description: description.trim() || undefined,
      });
      setEditing(false);
      onTaskUpdated();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update task');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setTitle(task.title);
    setDescription(task.description || '');
    setEditing(false);
    setError('');
  };

  return (
    <div className={`bg-white p-4 rounded-lg shadow-md mb-3 ${task.completed ? 'opacity-60' : ''}`}>
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-2 rounded mb-3">
          {error}
        </div>
      )}

      {editing ? (
        <form onSubmit={handleSave} className="space-y-3">
          <div>
            <label htmlFor={`edit-title-${task.id}`} className="block text-sm font-medium text-gray-700 mb-1">
              Title *
            </label>
            <input
              id={`edit-title-${task.id}`}
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label htmlFor={`edit-description-${task.id}`} className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              id={`edit-description-${task.id}`}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={2}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="flex gap-2">
            <button
              type="submit"
              disabled={loading}
              className="bg-blue-600 text-white py-1 px-3 rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Saving...' : 'Save'}
            </button>
            <button
              type="button"
              onClick={handleCancel}
              className="bg-gray-200 text-gray-700 py-1 px-3 rounded hover:bg-gray-300"
            >
              Cancel
            </button>
          </div>
        </form>
      ) : (
        <div className="space-y-2">
          <div className="flex items-start justify-between gap-3">
            <div className="flex-1">
              <h3 className={`text-lg font-semibold ${task.completed ? 'line-through text-gray-500' : ''}`}>
                {task.title}
              </h3>
              {task.description && (
                <p className="text-gray-600 text-sm mt-1">{task.description}</p>
              )}
              <p className="text-xs text-gray-400 mt-2">
                Created: {new Date(task.created_at).toLocaleDateString()}
              </p>
            </div>

            <div className="flex flex-col gap-2">
              <button
                onClick={handleToggleComplete}
                disabled={loading}
                className={`px-3 py-1 rounded text-sm font-medium ${
                  task.completed
                    ? 'bg-green-100 text-green-700 hover:bg-green-200'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                {task.completed ? '✓ Done' : '○ Complete'}
              </button>
              <button
                onClick={() => setEditing(true)}
                className="bg-blue-100 text-blue-700 px-3 py-1 rounded text-sm font-medium hover:bg-blue-200"
              >
                Edit
              </button>
              <button
                onClick={handleDelete}
                disabled={loading}
                className="bg-red-100 text-red-700 px-3 py-1 rounded text-sm font-medium hover:bg-red-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
