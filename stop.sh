#!/bin/bash
#
# XILFTEN Application Stop Script
# Cleanly stops all XILFTEN server processes
#

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  XILFTEN Application Stop${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to kill existing XILFTEN server processes
kill_xilften_servers() {
    echo -e "${BLUE}🔍 Checking for XILFTEN server processes...${NC}"

    # Find processes running backend/server.py
    local server_pids=$(pgrep -f "backend/server.py" 2>/dev/null || true)

    if [ -n "$server_pids" ]; then
        echo -e "${YELLOW}⚠️  Found XILFTEN server processes: ${server_pids}${NC}"
        for pid in $server_pids; do
            echo -e "${YELLOW}🔫 Killing process ${pid}...${NC}"
            if kill -9 ${pid} 2>/dev/null; then
                echo -e "${GREEN}✅ Process ${pid} killed${NC}"
            else
                echo -e "${RED}❌ Failed to kill process ${pid}${NC}"
            fi
        done
        sleep 1
        echo -e "${GREEN}✅ All XILFTEN servers stopped${NC}"
    else
        echo -e "${GREEN}✅ No XILFTEN server processes found${NC}"
    fi
}

# Kill all XILFTEN servers
kill_xilften_servers

# Check port 7575
PORT=7575
echo ""
echo -e "${BLUE}🔍 Checking if port ${PORT} is still in use...${NC}"
PORT_PID=$(lsof -ti:${PORT} 2>/dev/null || true)

if [ -n "$PORT_PID" ]; then
    echo -e "${YELLOW}⚠️  Port ${PORT} is still in use by process ${PORT_PID}${NC}"
    echo -e "${YELLOW}🔫 Killing process ${PORT_PID}...${NC}"
    kill -9 ${PORT_PID} 2>/dev/null && echo -e "${GREEN}✅ Process killed${NC}"
else
    echo -e "${GREEN}✅ Port ${PORT} is free${NC}"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  ✨ XILFTEN stopped successfully${NC}"
echo -e "${BLUE}========================================${NC}"
