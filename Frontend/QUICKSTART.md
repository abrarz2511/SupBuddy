# 🚀 Quick Start Guide - SupBuddy Frontend

## What You Need Right Now to Run the Frontend

Follow these steps to get the React dashboard running:

---

## Step 1: Install Node.js Dependencies

```bash
cd Frontend
npm install
```

This will install all required packages:
- React & React DOM
- TypeScript
- Material-UI components
- Axios for API calls
- React Query for data fetching
- Recharts for visualizations
- Vite for development server

**Expected time**: 2-3 minutes

---

## Step 2: Verify Environment Configuration

The `.env` file is already created with default settings:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
VITE_REFRESH_INTERVAL=30000
VITE_ENABLE_AUTO_REFRESH=true
```

✅ **No changes needed** if your backend runs on `http://localhost:8000`

---

## Step 3: Start the Backend API (Required)

The frontend needs the backend API to be running. In a separate terminal:

```bash
cd Backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Verify backend is running:
- Open http://localhost:8000/docs
- You should see the FastAPI Swagger documentation

---

## Step 4: Start the Frontend Development Server

```bash
npm run dev
```

You should see output like:

```
  VITE v5.0.8  ready in 500 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

---

## Step 5: Open in Browser

Navigate to: **http://localhost:3000**

You should see:
- ✅ SupBuddy Dashboard header
- ✅ "Frontend Setup Complete!" message
- ✅ List of completed features
- ✅ Three feature cards (Shipments, Alerts, AI Analysis)

---

## What's Working Right Now

### ✅ Fully Functional
- TypeScript compilation
- Vite development server with hot reload
- Material-UI theming and components
- React Query setup for data fetching
- API client with error handling
- Environment configuration

### 🚧 Coming Soon
- Dashboard layout with real data
- Shipments widget showing active shipments
- Alerts widget with filtering
- AI analysis panel
- Data visualization charts

---

## Troubleshooting

### Issue: `npm install` fails

**Solution**: Check Node.js version
```bash
node --version  # Should be v18+ or v20+
npm --version   # Should be v9+ or v10+
```

If outdated, download from: https://nodejs.org/

---

### Issue: Port 3000 already in use

**Solution**: Vite will automatically use the next available port (3001, 3002, etc.)

Or manually specify a port:
```bash
npm run dev -- --port 3001
```

---

### Issue: Cannot connect to backend API

**Symptoms**: Console errors about network requests failing

**Solution**:
1. Verify backend is running: http://localhost:8000/docs
2. Check `.env` has correct `VITE_API_BASE_URL`
3. Ensure no firewall blocking localhost connections

---

### Issue: TypeScript errors in VS Code

**Solution**: These are expected before `npm install`. After installing dependencies, restart VS Code:
- Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
- Type "Reload Window"
- Press Enter

---

### Issue: Blank page or errors in browser

**Solution**:
1. Open browser DevTools (F12)
2. Check Console tab for errors
3. Check Network tab for failed API calls
4. Clear browser cache and reload (Ctrl+Shift+R)

---

## Development Workflow

### Making Changes

1. **Edit files** in `src/` directory
2. **Save** - Changes appear instantly (hot reload)
3. **Check browser** - Updates automatically
4. **Check console** - For any errors

### File Structure

```
src/
├── api/          ← API calls to backend
├── types/        ← TypeScript type definitions
├── config/       ← Configuration files
├── theme/        ← Material-UI theme
├── App.tsx       ← Main app component
└── main.tsx      ← Entry point
```

### Adding New Features

1. **Types**: Define in `src/types/`
2. **API**: Add calls in `src/api/`
3. **Components**: Create in `src/components/` (to be created)
4. **Hooks**: Add in `src/hooks/` (to be created)

---

## Next Development Steps

### 1. Create Dashboard Layout
```bash
# Create components directory
mkdir -p src/components/layout
```

### 2. Add Shipments Widget
```bash
mkdir -p src/components/shipments
```

### 3. Add Alerts Widget
```bash
mkdir -p src/components/alerts
```

### 4. Add AI Analysis Panel
```bash
mkdir -p src/components/analysis
```

---

## Useful Commands

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint

# Install new package
npm install package-name

# Update dependencies
npm update
```

---

## Environment Variables

Edit `.env` to customize:

```env
# Change API URL
VITE_API_BASE_URL=http://your-api-url:8000

# Change refresh interval (milliseconds)
VITE_REFRESH_INTERVAL=60000  # 1 minute

# Disable auto-refresh
VITE_ENABLE_AUTO_REFRESH=false

# Enable WebSocket (when implemented)
VITE_ENABLE_WEBSOCKET=true
```

**Note**: Restart dev server after changing `.env`

---

## Browser DevTools Tips

### Console Tab
- View logs and errors
- Check API responses
- Debug React components

### Network Tab
- Monitor API calls
- Check request/response data
- Verify backend connectivity

### React DevTools Extension
Install for better debugging:
- Chrome: https://chrome.google.com/webstore (search "React Developer Tools")
- Firefox: https://addons.mozilla.org/firefox/ (search "React Developer Tools")

---

## Success Checklist

Before continuing development, verify:

- [ ] `npm install` completed successfully
- [ ] Backend API running on http://localhost:8000
- [ ] Frontend running on http://localhost:3000
- [ ] Dashboard page loads without errors
- [ ] Browser console shows no errors
- [ ] Hot reload works (edit App.tsx and see changes)

---

## Getting Help

### Check Documentation
- `README.md` - Full documentation
- `TECHNICAL_SPEC.md` - Technical details
- `ARCHITECTURE.md` - System architecture

### Common Issues
- Backend not running → Start backend first
- Port conflicts → Use different port
- TypeScript errors → Run `npm install`
- Build errors → Delete `node_modules` and reinstall

---

## Summary

**You're ready to run the frontend when:**

1. ✅ Dependencies installed (`npm install`)
2. ✅ Backend API running (port 8000)
3. ✅ Frontend dev server started (`npm run dev`)
4. ✅ Browser shows dashboard (port 3000)

**Current Status**: Foundation complete, ready for UI component development!

---

**Need more help?** Check the main `README.md` or `TECHNICAL_SPEC.md` files.