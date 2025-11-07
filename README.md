# Growgent

Open-source agentic platform for climate-adaptive irrigation and wildfire management.

## Project Structure

```
growgent/
├── frontend/          # Next.js frontend (currently Vite, migrating to Next.js)
│   ├── app/           # Next.js App Router (to be created)
│   ├── components/    # React components
│   ├── styles/        # Global styles
│   ├── public/        # Static assets
│   └── package.json
│
├── backend/            # FastAPI backend
│   ├── app/
│   │   ├── main.py     # FastAPI initialization
│   │   ├── config.py   # Settings
│   │   ├── models/     # SQLAlchemy models
│   │   ├── schemas/    # Pydantic models
│   │   ├── api/        # API routes
│   │   ├── agents/     # LangGraph agents
│   │   ├── mcp/        # MCP servers
│   │   ├── services/   # Business logic
│   │   └── utils/
│   ├── tests/          # Backend tests
│   ├── requirements.txt
│   └── Dockerfile
│
├── Product Documents/  # Product requirements and documentation
├── Coding Agent Rules/ # Cursor and CodeRabbit configuration
└── LICENSE.md
```

## Quick Start

### Frontend (Vite - migrating to Next.js)

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:3000`

### Backend (FastAPI)

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend API runs on `http://localhost:8000`

API documentation available at `http://localhost:8000/docs`

## Development

See `Product Documents/Growgent_Technical_PRD.md` for full technical specifications.

See `Coding Agent Rules/.cursorrules` for development guidelines and coding standards.

## License

AGPL v3 - See LICENSE.md
