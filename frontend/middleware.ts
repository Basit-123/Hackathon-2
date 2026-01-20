import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Simple routing logic for the proxy system
export function middleware(request: NextRequest) {
  // Allow all requests to pass through - authentication is handled client-side
  return NextResponse.next();
}

// Match all routes for simple proxy behavior
export const config = {
  matcher: ['/:path*']
};
