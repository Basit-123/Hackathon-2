'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { getJWT, getUserIdFromToken } from '@/lib/api';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Check if user is authenticated
    const token = getJWT();
    const userId = getUserIdFromToken();

    if (token && userId) {
      // Redirect to tasks page
      router.push('/tasks');
    } else {
      // Redirect to signin page
      router.push('/signin');
    }
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
        <p className="mt-4 text-gray-600">Loading...</p>
      </div>
    </div>
  );
}
