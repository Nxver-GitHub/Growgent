# Frontend Debugging Guide

## ✅ Fixed Issues

### 1. **Port Configuration**
- ✅ Updated `vite.config.ts` to use port **3001**
- ✅ Backend CORS already allows `http://localhost:3001`
- ✅ Server configured to not auto-open browser

### 2. **Error Handling**
- ✅ Added comprehensive error handling in `main.tsx`
- ✅ Added console logging for debugging
- ✅ Added user-friendly error messages
- ✅ Error boundaries in place

### 3. **HTML Structure**
- ✅ Fixed `index.html` formatting
- ✅ Added loading indicator for empty root
- ✅ Added proper meta tags and styling

## 🔍 Debugging Steps

### If you see a blank screen:

1. **Open Browser Console (F12)**
   - Look for console logs:
     - `🚀 Growgent Frontend: Initializing application...`
     - `✅ Root element found, creating React root...`
     - `✅ Rendering App component...`
     - `✅ Application rendered successfully!`
     - `📱 App component rendering...`

2. **Check for Errors**
   - Red errors in console = JavaScript/TypeScript errors
   - Network errors = API connection issues
   - CORS errors = Backend not allowing frontend origin

3. **Verify Server is Running**
   ```powershell
   # Check if port 3001 is listening
   netstat -ano | findstr :3001
   
   # Test server response
   Invoke-WebRequest -Uri http://localhost:3001 -UseBasicParsing
   ```

4. **Check Network Tab**
   - Open DevTools → Network tab
   - Refresh page
   - Look for failed requests (red)
   - Check if `main.tsx` loads successfully

5. **Verify Backend Connection**
   - Backend should be running on `http://localhost:8000`
   - Check CORS allows `http://localhost:3001`
   - Test backend health: `curl http://localhost:8000/health`

## 🚀 Starting the Server

```powershell
# Navigate to frontend directory
cd frontend

# Start development server
npm run dev
```

The server will start on `http://localhost:3001`

## 📋 Expected Console Output

When everything works correctly, you should see:

```
🚀 Growgent Frontend: Initializing application...
✅ Root element found, creating React root...
✅ Rendering App component...
✅ Application rendered successfully!
📱 App component rendering...
```

## 🐛 Common Issues

### Issue: Blank Screen with No Console Logs
**Solution**: Check if `main.tsx` is loading. Open Network tab and verify `/main.tsx` returns 200.

### Issue: CORS Errors
**Solution**: Ensure backend `ALLOWED_ORIGINS` includes `http://localhost:3001`

### Issue: Module Not Found Errors
**Solution**: Run `npm install` to ensure all dependencies are installed.

### Issue: React Component Errors
**Solution**: Check browser console for specific component errors. Error boundaries should catch these.

## 🔧 Quick Fixes

1. **Clear Browser Cache**: Hard refresh (Ctrl+Shift+R)
2. **Restart Dev Server**: Stop and restart `npm run dev`
3. **Reinstall Dependencies**: `rm -rf node_modules && npm install`
4. **Check TypeScript**: Run `npm run type-check`

## 📞 Next Steps

If you still see a blank screen after checking all above:
1. Share the browser console errors
2. Share the Network tab showing failed requests
3. Verify backend is running and accessible

