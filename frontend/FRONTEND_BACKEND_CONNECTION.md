# Frontend-Backend Connection Status

## ✅ Fixed Issues

1. **Missing Dependency**: Installed `@tanstack/react-query` package
2. **Sonner Component**: Fixed import to work with Vite (removed Next.js-specific code)
3. **Frontend Server**: Now running successfully on `http://localhost:3000`

## 🔧 Current Status

### Frontend
- ✅ Running on `http://localhost:3000`
- ✅ All dependencies installed
- ✅ React Query configured
- ✅ API client ready to connect

### Backend
- ⚠️ **Needs to be started manually**

## 🚀 Starting the Backend

Open a **new terminal** and run:

```powershell
cd Backend
.\venv\Scripts\activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

## 🧪 Testing the Connection

### 1. Test Backend Health
```powershell
curl http://localhost:8000/health
```
Expected: `{"status":"healthy"}`

### 2. Test API Endpoints
```powershell
# Fields endpoint
curl http://localhost:8000/api/fields

# Critical alerts
curl http://localhost:8000/api/alerts/critical?limit=5

# Recommendations
curl http://localhost:8000/api/agents/irrigation/recommendations?page=1&page_size=5
```

### 3. Test Frontend-Backend Connection

1. Open browser to `http://localhost:3000`
2. Open Developer Console (F12)
3. Go to Network tab
4. Check for API requests:
   - Should see requests to `/api/alerts/critical`
   - Should see requests to `/api/agents/irrigation/recommendations`
   - Should see requests to `/api/fields`
5. Check Console tab for any errors

## 📋 API Endpoints Configured

The frontend is configured to call these endpoints:

| Endpoint | Purpose | Component |
|----------|---------|-----------|
| `/api/alerts/critical` | Get critical alerts | Dashboard |
| `/api/alerts` | List all alerts | Alerts page |
| `/api/alerts/{id}/acknowledge` | Acknowledge alert | Alerts page |
| `/api/agents/irrigation/recommendations` | Get recommendations | Dashboard, Schedule |
| `/api/recommendations/{id}/accept` | Accept recommendation | RecommendationModal |
| `/api/fields` | List fields | Dashboard, Schedule |
| `/api/fields/{id}` | Get field details | FieldsMap |
| `/api/metrics/water` | Water metrics | WaterMetrics |
| `/api/metrics/fire-risk` | Fire risk metrics | FireRiskMetrics |

## 🔍 Troubleshooting

### Frontend shows "Failed to load dashboard data"
- **Check**: Is backend running on port 8000?
- **Fix**: Start backend server (see above)

### CORS Errors in Browser Console
- **Check**: Backend CORS configuration in `Backend/app/main.py`
- **Fix**: Ensure `localhost:3000` is in `ALLOWED_ORIGINS`

### API Returns 404
- **Check**: Endpoint path matches backend routes
- **Fix**: Verify endpoint in `Backend/app/api/` files

### API Returns 500
- **Check**: Database is running and initialized
- **Fix**: Run `python Backend/scripts/init_database.py`

### No Data Displayed
- **Check**: Database has data (fields, alerts, recommendations)
- **Fix**: Add test data or check database connection

## ✅ Success Indicators

When everything is working:
- ✅ Frontend loads without errors
- ✅ Dashboard shows data (or "No data" message)
- ✅ Network tab shows successful API calls (200 status)
- ✅ No CORS errors in console
- ✅ React Query DevTools shows queries (if installed)

## 📝 Next Steps

1. Start backend server
2. Verify backend health endpoint
3. Open frontend in browser
4. Check browser console for errors
5. Verify API calls in Network tab
6. Test user interactions (acknowledge alerts, accept recommendations)

