#!/bin/bash
#
# XILFTEN Application Startup Script
# Port: 7575 (ENFORCED - See CLAUDE.md)
#
# This script:
# 1. Kills any existing XILFTEN server processes
# 2. Checks if port 7575 is in use
# 3. Kills any process using that port
# 4. Starts the XILFTEN application
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PORT=7575
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="${SCRIPT_DIR}"
PYTHON_PATH="${APP_DIR}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  XILFTEN Application Startup${NC}"
echo -e "${BLUE}  Port: ${PORT}${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to kill existing XILFTEN server processes
kill_existing_servers() {
    echo -e "${BLUE}🔍 Checking for existing XILFTEN server processes...${NC}"

    # Find processes running backend/server.py
    local server_pids=$(pgrep -f "backend/server.py" 2>/dev/null || true)

    if [ -n "$server_pids" ]; then
        echo -e "${YELLOW}⚠️  Found existing XILFTEN server processes: ${server_pids}${NC}"
        for pid in $server_pids; do
            echo -e "${YELLOW}🔫 Killing process ${pid}...${NC}"
            if kill -9 ${pid} 2>/dev/null; then
                echo -e "${GREEN}✅ Process ${pid} killed${NC}"
            fi
        done
        sleep 2
    else
        echo -e "${GREEN}✅ No existing XILFTEN server processes found${NC}"
    fi
}

# Function to check if port is in use
check_port() {
    lsof -ti:${PORT} 2>/dev/null || true
}

# Function to kill process on port
kill_port_process() {
    local pid=$1
    echo -e "${YELLOW}⚠️  Port ${PORT} is in use by process ${pid}${NC}"
    echo -e "${YELLOW}🔫 Attempting to kill process ${pid}...${NC}"

    # Try graceful kill first
    if kill ${pid} 2>/dev/null; then
        echo -e "${GREEN}✅ Process ${pid} killed gracefully${NC}"
        sleep 2
    else
        # Force kill if graceful fails
        echo -e "${YELLOW}⚠️  Graceful kill failed, forcing...${NC}"
        if kill -9 ${pid} 2>/dev/null; then
            echo -e "${GREEN}✅ Process ${pid} force killed${NC}"
            sleep 2
        else
            echo -e "${RED}❌ Failed to kill process ${pid}${NC}"
            echo -e "${RED}   You may need to run this script with sudo${NC}"
            exit 1
        fi
    fi
}

# First, kill any existing XILFTEN server processes
kill_existing_servers

echo ""

# Check if port is in use
echo -e "${BLUE}🔍 Checking if port ${PORT} is in use...${NC}"
PORT_PID=$(check_port)

if [ -n "$PORT_PID" ]; then
    # Port is in use
    kill_port_process ${PORT_PID}

    # Verify port is now free
    sleep 1
    PORT_PID=$(check_port)
    if [ -n "$PORT_PID" ]; then
        echo -e "${RED}❌ Port ${PORT} is still in use after kill attempt${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Port ${PORT} is now free${NC}"
else
    echo -e "${GREEN}✅ Port ${PORT} is free${NC}"
fi

echo ""

# Change to application directory
echo -e "${BLUE}📂 Changing to application directory...${NC}"
cd "${APP_DIR}" || {
    echo -e "${RED}❌ Failed to change to directory: ${APP_DIR}${NC}"
    exit 1
}
echo -e "${GREEN}✅ Current directory: $(pwd)${NC}"

echo ""

# Source environment keys if available
if [ -f "$HOME/keys.sh" ]; then
    echo -e "${BLUE}🔑 Sourcing environment keys from ~/keys.sh...${NC}"
    source "$HOME/keys.sh"
    echo -e "${GREEN}✅ Environment keys loaded${NC}"
else
    echo -e "${YELLOW}⚠️  ~/keys.sh not found - using existing environment variables${NC}"
fi

echo ""

# Start the application
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  🚀 Starting XILFTEN Application${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}📍 Frontend: http://localhost:${PORT}${NC}"
echo -e "${GREEN}📍 API Docs: http://localhost:${PORT}/docs${NC}"
echo -e "${GREEN}📍 Health Check: http://localhost:${PORT}/api/health${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Set PYTHONPATH and run the application
export PYTHONPATH="${PYTHON_PATH}"

# Run with UV
exec uv run python backend/server.py
