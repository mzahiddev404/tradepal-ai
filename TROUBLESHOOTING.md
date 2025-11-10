# Troubleshooting

## macOS Turbopack Permission Error

**Problem**: `Error [TurbopackInternalError]: reading dir /Users/muhammad/Desktop - Operation not permitted`

**Cause**: macOS Sonoma+ Desktop security + parent lockfile at `/Users/muhammad/package-lock.json`

**Solutions**:

### Option 1: Move Project (Recommended)
```bash
cd ~
mv "Desktop/ASU School/AZNext ASU AI Vibe Coding/tradepal-ai" ~/tradepal-ai
cd ~/tradepal-ai/frontend && npm run dev
```

### Option 2: Grant Terminal Full Disk Access
System Settings → Privacy & Security → Full Disk Access → Add Terminal

### Option 3: Remove Parent Lockfile
```bash
mv /Users/muhammad/package-lock.json /Users/muhammad/package-lock.json.backup
cd tradepal-ai/frontend && npm run dev
```

## Other Issues

**Port in use**:
```bash
lsof -ti:3000 | xargs kill -9
```

**Clear cache**:
```bash
cd frontend && rm -rf .next node_modules && npm install
```

