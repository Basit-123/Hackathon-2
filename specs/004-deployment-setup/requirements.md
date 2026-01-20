# Deployment Setup Requirements

**Purpose**: High-level requirements for deploying Todo app to production platforms

## What We Need

The application needs deployment configuration for:

1. **Frontend Deployment**
   - Vercel platform for Next.js hosting
   - Environment variable configuration
   - Build and deployment process

2. **Backend Deployment**
   - Render or Fly.io platform for FastAPI hosting
   - Environment variable configuration
   - Start command (uvicorn)

3. **Database Setup**
   - Neon PostgreSQL connection
   - DATABASE_URL configuration

4. **Environment Variables**
   - Shared BETTER_AUTH_SECRET
   - API URL configuration
   - Database connection string

## Success Criteria

- Frontend deploys to Vercel successfully
- Backend deploys to Render/Fly.io successfully
- Neon database is accessible
- All environment variables are configured
- Application is accessible from production URLs
