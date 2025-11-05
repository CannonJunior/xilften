# XILFTEN Startup Guide

## Quick Start

### Using the Startup Script (Recommended)

```bash
cd /home/junior/src/xilften
./start.sh
```

The `start.sh` script automatically handles:
- ✅ Port 7575 availability check
- ✅ Killing existing processes on that port
- ✅ Setting up the correct Python environment
- ✅ Starting the XILFTEN application

### Manual Startup

If you prefer to start manually:

```bash
cd /home/junior/src/xilften
PYTHONPATH=/home/junior/src/xilften uv run python backend/server.py
```

## Accessing the Application

Once started, the application is available at:

- **Frontend**: http://localhost:7575
- **API Documentation**: http://localhost:7575/docs
- **Health Check**: http://localhost:7575/api/health
- **API Root**: http://localhost:7575/api

## Script Features

### Port Management

The start.sh script includes intelligent port management:

1. **Checks if port 7575 is in use**
   - Uses `lsof` to detect processes on port 7575

2. **Graceful process termination**
   - Attempts graceful kill first (`kill <pid>`)
   - Falls back to force kill if needed (`kill -9 <pid>`)
   - Waits 2 seconds after killing to ensure port is free

3. **Verification**
   - Confirms port is free before starting application
   - Exits with error if port cannot be freed

### Colored Output

The script uses colored output for easy reading:
- 🔵 **Blue**: Section headers and informational messages
- 🟢 **Green**: Success messages and confirmations
- 🟡 **Yellow**: Warnings and important notes
- 🔴 **Red**: Errors and failures

### Environment Setup

The script automatically:
- Changes to the application directory
- Sets `PYTHONPATH` environment variable
- Creates `.env` from `.env.example` if missing
- Starts the application with UV package manager

## Stopping the Application

To stop the running server:

1. **If running in foreground**: Press `Ctrl+C`
2. **If running in background**:
   ```bash
   lsof -ti:7575 | xargs kill
   ```
3. **Force kill if needed**:
   ```bash
   lsof -ti:7575 | xargs kill -9
   ```

## Troubleshooting

### Port Already in Use

If you see an error about port 7575 being in use:

```bash
# Check what's using the port
lsof -i:7575

# Kill the process
lsof -ti:7575 | xargs kill -9

# Then run start.sh again
./start.sh
```

### Permission Denied

If you get a "Permission denied" error:

```bash
# Make the script executable
chmod +x start.sh

# Then run it
./start.sh
```

### Missing Dependencies

If you see import errors:

```bash
# Sync dependencies with UV
uv sync

# Then run start.sh
./start.sh
```

### Database Not Initialized

If you see warnings about missing tables:

```bash
# This is expected for Phase 1
# Database migrations will be created in Phase 2
# The application will still run with sample data
```

## Development Mode

The application runs in **debug mode** by default, which includes:

- **Hot reload**: Server auto-restarts when files change
- **Detailed logging**: See all API requests and errors
- **Interactive API docs**: Full Swagger UI at `/docs`

To disable debug mode, edit `.env`:

```bash
DEBUG=false
```

## Configuration

### Environment Variables

Key environment variables in `.env`:

```bash
# Application
APP_HOST=0.0.0.0
APP_PORT=7575  # CRITICAL: Do not change without permission
DEBUG=true

# TMDB API
TMDB_API_KEY=your_key_here  # Get from https://www.themoviedb.org/settings/api

# Ollama (AI Features)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=qwen2.5:3b

# Database
DUCKDB_DATABASE_PATH=./database/xilften.duckdb
CHROMA_PERSIST_DIRECTORY=./database/chroma_data
```

### Port 7575 - CRITICAL

⚠️ **The application MUST run on port 7575**

This is enforced in the code via Pydantic validation. Attempting to change the port will result in a validation error. See `CLAUDE.md` for details.

## Next Steps

After starting the application:

1. **Configure TMDB API key** in `.env` (optional but recommended)
2. **Install Ollama** for AI features (optional)
   ```bash
   ollama pull qwen2.5:3b
   ```
3. **Open the frontend** at http://localhost:7575
4. **Explore the API docs** at http://localhost:7575/docs

## Health Check

To verify the application is running correctly:

```bash
curl http://localhost:7575/api/health
```

Expected response:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "version": "0.1.0",
    "timestamp": "2025-11-04T...",
    "services": {
      "database": "connected",
      "chromadb": "connected",
      "ollama": "unknown",
      "tmdb": "unknown"
    }
  }
}
```

## Support

For issues or questions:
- Check `README.md` for detailed documentation
- Review `PROGRESS-SUMMARY.md` for current status
- See `TASK.md` for planned features

---

**Last Updated**: 2025-11-03
**Script Version**: 1.0.0
