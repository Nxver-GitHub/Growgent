# Testing Frontend-Backend Connection

## Current Status

✅ **PostgreSQL Database**: Running on port 5433
✅ **Frontend Dependencies**: Installed
⚠️ **Backend API**: Needs to be started manually

## Steps to Test the Connection

### 1. Start the Backend API Server

Open a terminal in the `Backend` directory and run:

```powershell
# Activate virtual environment
.\venv\Scripts\activate.ps1

# Start the FastAPI server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Database initialized successfully
INFO:     Application startup complete.
```

### 2. Verify Backend is Running

In another terminal, test the health endpoint:

```powershell
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"healthy"}
```

### 3. Start the Frontend

Open a terminal in the `frontend` directory and run:

```powershell
npm run dev
```

The frontend should start on `http://localhost:3000` (as configured in vite.config.ts)

### 4. Test the Connection

1. Open your browser to `http://localhost:3000`
2. Open the browser's Developer Console (F12)
3. Check the Network tab for API requests
4. The Dashboard should attempt to fetch:
   - `/api/alerts/critical`
   - `/api/agents/irrigation/recommendations`
   - `/api/fields`

### 5. Expected Behavior

**If everything is working:**
- Dashboard loads with data from the backend
- No CORS errors in the console
- API requests return 200 status codes
- Data displays in the UI

**If there are issues:**
- Check browser console for errors
- Verify backend is running on port 8000
- Check CORS configuration in `Backend/app/main.py`
- Ensure `.env.local` has `VITE_API_BASE_URL=http://localhost:8000`

## Troubleshooting

### Backend won't start
- Check if virtual environment is activated
- Verify dependencies are installed: `pip install -r requirements.txt`
- Check if database is initialized: `python scripts/init_database.py`
- Check for port conflicts (port 8000 might be in use)

### CORS Errors
- Backend CORS is configured for `localhost:3000` and `localhost:5173`
- If using a different port, update `Backend/app/main.py` ALLOWED_ORIGINS

### API Returns 404
- Verify the endpoint path matches what's in `frontend/lib/constants.ts`
- Check backend routes in `Backend/app/api/` files

### No Data Displayed
- Check if database has data (fields, alerts, recommendations)
- Verify API responses in browser Network tab
- Check React Query DevTools for query states

## Quick Test Commands

```powershell
# Test backend health
curl http://localhost:8000/health

# Test fields endpoint
curl http://localhost:8000/api/fields

# Test alerts endpoint
curl http://localhost:8000/api/alerts/critical?limit=5

# Test recommendations endpoint
curl http://localhost:8000/api/agents/irrigation/recommendations?page=1&page_size=5
```

