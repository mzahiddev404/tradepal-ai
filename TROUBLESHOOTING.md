# Troubleshooting Guide - TradePal AI

Common issues and their solutions.

## Backend Issues

### Server Won't Start

**Problem**: Backend server fails to start or crashes immediately.

**Solutions**:
1. Check Python version: `python3 --version` (should be 3.13+)
2. Verify virtual environment is activated
3. Check if port 8000 is available: `lsof -ti:8000`
4. Review error logs in terminal output
5. Verify all dependencies installed: `pip list`

### Import Errors

**Problem**: `ModuleNotFoundError` or `ImportError` when starting server.

**Solutions**:
1. Ensure virtual environment is activated
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Check Python path includes backend directory
4. Verify `__init__.py` files exist in all packages
5. Try: `pip install --upgrade pip` then reinstall

### API Key Errors

**Problem**: "Invalid API key" or "API key not found" errors.

**Solutions**:
1. Verify `.env` file exists in `backend/` directory
2. Check API keys are set correctly (no quotes, no spaces)
3. Restart server after changing `.env` file
4. Verify API keys are valid and have credits
5. Check environment variable names match exactly

### ChromaDB Errors

**Problem**: ChromaDB initialization fails or database errors.

**Solutions**:
1. Delete and recreate database: `rm -rf backend/chroma_db/`
2. Check disk space availability
3. Verify write permissions on backend directory
4. Try reinstalling ChromaDB: `pip install --upgrade chromadb`
5. Check ChromaDB logs for specific errors

### Agent Routing Issues

**Problem**: Queries not routing to correct agents.

**Solutions**:
1. Check orchestrator logs for routing decisions
2. Verify AWS Bedrock credentials if using (or check OpenAI fallback)
3. Review query classification logic in `orchestrator.py`
4. Test individual agents directly
5. Check LangGraph workflow configuration

## Frontend Issues

### Build Errors

**Problem**: `npm run build` fails with TypeScript or build errors.

**Solutions**:
1. Clear cache: `rm -rf .next node_modules`
2. Reinstall dependencies: `npm install`
3. Check Node.js version: `node --version` (should be 18+)
4. Review TypeScript errors in terminal
5. Verify all imports are correct

### API Connection Errors

**Problem**: Frontend can't connect to backend API.

**Solutions**:
1. Verify backend is running on port 8000
2. Check `NEXT_PUBLIC_API_URL` in `.env.local`
3. Verify CORS is configured correctly in backend
4. Check browser console for specific error messages
5. Test API directly: `curl http://localhost:8000/api/health`

### Component Rendering Issues

**Problem**: Components not rendering or showing errors.

**Solutions**:
1. Check browser console for errors
2. Verify all imports are correct
3. Check component props match expected types
4. Review React DevTools for component state
5. Clear browser cache and hard refresh

### Hot Reload Not Working

**Problem**: Changes not reflecting in browser.

**Solutions**:
1. Restart dev server: `npm run dev`
2. Clear `.next` directory: `rm -rf .next`
3. Check file watcher limits (especially on Linux)
4. Verify files are saved correctly
5. Try manual browser refresh

## API Issues

### Stock Data Not Loading

**Problem**: Stock quotes or historical data not returning.

**Solutions**:
1. Check Alpha Vantage API key is valid
2. Verify API rate limits haven't been exceeded
3. Check symbol is valid (e.g., TSLA, SPY)
4. Review error messages in API response
5. System will fallback to yfinance if Alpha Vantage fails

### PDF Upload Failing

**Problem**: PDF files not uploading or processing.

**Solutions**:
1. Verify file is valid PDF format
2. Check file size (max 10MB default)
3. Review upload endpoint logs
4. Check ChromaDB is running and accessible
5. Verify write permissions on backend directory

### Chat Responses Slow

**Problem**: Chat responses taking too long.

**Solutions**:
1. Check OpenAI API status and rate limits
2. Review agent routing logic (may be using wrong agent)
3. Check ChromaDB query performance
4. Verify network connectivity
5. Consider using streaming responses

## Testing Issues

### Tests Failing

**Problem**: Test suite fails to run or tests fail.

**Solutions**:
1. Install test dependencies: `pip install -r requirements-test.txt`
2. Verify pytest is installed: `pytest --version`
3. Check test environment variables are set
4. Review test output for specific errors
5. Run tests individually to isolate issues

### Import Errors in Tests

**Problem**: Tests can't import modules.

**Solutions**:
1. Verify `sys.path` includes backend directory
2. Check `conftest.py` path configuration
3. Run tests from backend directory
4. Verify all `__init__.py` files exist
5. Check Python path: `python -c "import sys; print(sys.path)"`

## Performance Issues

### Slow Response Times

**Problem**: Application feels slow or unresponsive.

**Solutions**:
1. Check API rate limits (OpenAI, Alpha Vantage)
2. Review ChromaDB query performance
3. Check network latency
4. Verify database indexes are created
5. Consider caching strategies

### High Memory Usage

**Problem**: Application using too much memory.

**Solutions**:
1. Check for memory leaks in long-running processes
2. Review ChromaDB collection sizes
3. Clear old session data
4. Monitor agent context caching
5. Consider implementing memory limits

## Environment-Specific Issues

### macOS Issues

**Problem**: Architecture mismatch errors (x86_64 vs arm64).

**Solutions**:
1. Use Rosetta 2 or native ARM64 Python
2. Recreate virtual environment: `rm -rf venv && python3 -m venv venv`
3. Reinstall dependencies for correct architecture
4. Use `fix_dependencies.sh` script if available

### Windows Issues

**Problem**: Path or permission errors.

**Solutions**:
1. Use forward slashes in paths
2. Run terminal as administrator if needed
3. Check Windows Defender isn't blocking files
4. Verify Python and Node are in PATH
5. Use Git Bash or WSL for better compatibility

### Linux Issues

**Problem**: Permission or file watcher errors.

**Solutions**:
1. Check file permissions: `chmod +x scripts/*`
2. Increase file watcher limit: `echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf`
3. Verify Python and Node are installed correctly
4. Check SELinux settings if applicable
5. Review system logs: `journalctl -xe`

## Getting Help

If issues persist:

1. Check error logs in terminal output
2. Review browser console for frontend errors
3. Check backend logs in `backend.log` if available
4. Review GitHub issues for similar problems
5. Verify all prerequisites are met
6. Check API service status pages

## Debugging Tips

### Enable Debug Logging

**Backend:**
```python
# In main.py, change logging level
logging.basicConfig(level=logging.DEBUG)
```

**Frontend:**
```javascript
// In browser console
localStorage.debug = '*'
```

### Test API Directly

```bash
# Health check
curl http://localhost:8000/api/health

# Chat endpoint
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "history": []}'
```

### Check Service Status

```bash
# Check if backend is running
ps aux | grep "python.*main.py"

# Check if frontend is running
ps aux | grep "next dev"

# Check port usage
lsof -i :8000  # Backend
lsof -i :3000  # Frontend
```

## Prevention

To avoid common issues:

1. Always use virtual environments for Python
2. Keep dependencies up to date
3. Use environment variables for all secrets
4. Test changes incrementally
5. Review logs regularly
6. Follow setup guide exactly
7. Keep API keys secure and rotated
