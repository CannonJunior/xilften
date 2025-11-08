#!/bin/bash
#
# XILFTEN Application Restart Script
# Stops and restarts the XILFTEN application
#

# Colors for output
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  XILFTEN Application Restart${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Stop the server
"${SCRIPT_DIR}/stop.sh"

echo ""
echo -e "${BLUE}⏳ Waiting 2 seconds before restart...${NC}"
sleep 2
echo ""

# Start the server
"${SCRIPT_DIR}/start.sh"
