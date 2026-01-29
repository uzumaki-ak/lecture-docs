# Supabase Authentication Setup Guide

## Overview

This guide explains the new Supabase-based authentication system for LectureDocs. The frontend has simple auth pages (login/signup), middleware to protect the dashboard, and the backend integrates with Supabase for user management.

## Frontend Setup

### 1. Install Dependencies

The package.json has already been updated with Supabase packages:

```bash
cd frontend
npm install
```

### 2. Configure Environment Variables

Update `frontend/.env` with your Supabase credentials:

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

**Where to get these values:**

1. Go to [supabase.com](https://supabase.com)
2. Create a new project
3. Go to Settings → API
4. Copy the "Project URL" and "anon public" key
5. Paste them into `.env`

### 3. What's New

#### Auth Pages

- **`app/auth/login/page.tsx`** - Simple login page
- **`app/auth/signup/page.tsx`** - Simple signup page with validation
- Users must sign up/login before accessing the dashboard

#### Middleware Protection

- **`middleware.ts`** - Protects `/dashboard/*` routes
- Redirects unauthenticated users to `/auth/login`
- Redirects authenticated users away from auth pages

#### Supabase Client

- **`lib/supabase.ts`** - Client-side Supabase functions
  - `signUp(email, password, name)`
  - `signIn(email, password)`
  - `signOut()`
  - `getSession()`

#### Updated Components

- **`Navbar.tsx`** - Now has a logout dropdown menu
- **`Providers.tsx`** - Removed Clerk, now handles Supabase auth state

## Backend Setup

### 1. Update Requirements

Install the new Supabase package:

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Update `backend/.env` with your Supabase credentials:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key-here
```

**Get Service Role Key:**

1. In Supabase console, go to Settings → API
2. Copy the "service_role" key (NOT the anon key)
3. Paste into `.env` as `SUPABASE_KEY`

### 3. Updated Auth Routes

The `/api/auth` endpoints now use Supabase:

**POST `/api/auth/signup`**

```json
{
  "email": "user@example.com",
  "password": "password123",
  "name": "John Doe"
}
```

- Creates user in Supabase
- Creates user record in local database
- Returns JWT token for local use

**POST `/api/auth/login`**

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

- Validates credentials with Supabase
- Creates or updates user in local database
- Returns JWT token for local use

## Flow Diagram

```
User → Login Page (app/auth/login)
         ↓
      Supabase.auth.signInWithPassword()
         ↓
      Backend /api/auth/login (optional)
         ↓
      localStorage.setItem("userEmail")
         ↓
      Middleware allows access to /dashboard
         ↓
      Dashboard Page (protected)
         ↓
      User clicks logout
         ↓
      Supabase.auth.signOut()
         ↓
      Middleware redirects to /auth/login
```

## Testing Locally

### 1. Start Backend

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8080
```

### 2. Start Frontend

```bash
cd frontend
npm run dev
```

### 3. Test Auth Flow

1. Go to `http://localhost:3000`
2. You'll be redirected to `/auth/login`
3. Click "Sign up" to create account
4. You'll receive a confirmation email
5. After verification, log in with credentials
6. You'll be redirected to `/dashboard`
7. Click logout in the account dropdown

## Key Features

✅ **Secure Authentication** - Uses Supabase's managed auth  
✅ **Dashboard Protection** - Middleware prevents unauthorized access  
✅ **Simple UI** - Clean login/signup pages  
✅ **Session Management** - Auto-refreshes tokens  
✅ **Fallback Auth** - Backend also validates with Supabase  
✅ **Database Integration** - Users synced to local database

## Troubleshooting

**"Supabase environment variables not configured"**

- Check that `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` are set in `frontend/.env`

**Middleware not redirecting**

- Clear browser cache
- Ensure middleware.ts is in the root of the project
- Restart dev server

**Backend auth failing**

- Check that `SUPABASE_URL` and `SUPABASE_KEY` are set in `backend/.env`
- Verify the keys are from the correct Supabase project
- Check backend console logs for errors

**Users can't verify email**

- Check Supabase email configuration in Settings → Authentication
- Users will have email confirmation enabled by default

## Next Steps

1. ✅ Replace Clerk environment variables with Supabase ones
2. ✅ Install dependencies (`npm install` in frontend, `pip install` in backend)
3. ✅ Test the auth flow locally
4. ✅ Deploy to production with proper environment variables
5. (Optional) Add OAuth providers (Google, GitHub) in Supabase console
6. (Optional) Customize email templates in Supabase Auth Settings
