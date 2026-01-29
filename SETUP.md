# Quick Setup

## Frontend

```bash
cd frontend
npm install
# Add to .env:
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
NEXT_PUBLIC_APP_URL=http://localhost:3000

npm run dev
```

## Backend

```bash
cd backend
pip install -r requirements.txt
# Add to .env:
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_service_role_key

python -m uvicorn app.main:app --reload --port 8080
```

## What Changed

- Frontend: Login/signup pages added, middleware protects dashboard
- Backend: Auth routes now use Supabase
- Users must sign in before accessing dashboard
- Logout button in navbar account menu

## Get Supabase Keys

1. Go to supabase.com → Create project
2. Settings → API → Copy "Project URL" and "anon public" key
3. Use service_role key for backend
