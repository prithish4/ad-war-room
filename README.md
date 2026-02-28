# Ad Intelligence Tool

A competitive ad intelligence platform that tracks, analyzes, and surfaces insights from competitor advertising activity using the Meta Ad Library API and Claude AI.

## Project Structure

```
ad-intelligence/
├── backend/          # FastAPI Python API server
│   ├── main.py       # App entrypoint, CORS, health check
│   ├── requirements.txt
│   └── .env.example
├── frontend/         # React + Vite + TypeScript dashboard
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── index.css
│   │   ├── lib/utils.ts
│   │   └── store/index.ts   # Zustand global state
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── .env.example
└── README.md
```

## Tech Stack

### Backend
| Package | Purpose |
|---------|---------|
| FastAPI | REST API framework |
| Uvicorn | ASGI server |
| HTTPX | Async HTTP client (Meta Ad Library) |
| supabase-py | Database & auth |
| anthropic | Claude AI analysis |
| python-dotenv | Environment config |
| APScheduler | Scheduled ad scraping jobs |

### Frontend
| Package | Purpose |
|---------|---------|
| React 18 + Vite | UI framework & build tool |
| TypeScript | Type safety |
| Recharts | Ad performance charts |
| React Query | Server state & caching |
| Zustand | Client-side global state |
| Tailwind CSS | Utility-first styling |
| shadcn/ui | Accessible component library |

## Getting Started

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # fill in your keys
uvicorn main:app --reload
```

API will be available at `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env            # set VITE_API_URL if needed
npm run dev
```

Dashboard will be available at `http://localhost:5173`.

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Claude API key for AI analysis |
| `META_ACCESS_TOKEN` | Meta Graph API token for Ad Library |
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_KEY` | Supabase anon/service key |

### Frontend (`frontend/.env`)

| Variable | Description |
|----------|-------------|
| `VITE_API_URL` | Base URL of the backend API |
