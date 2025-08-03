#!/bin/bash

# LangChain Dependencies Fix Script
# Resolves version conflicts between langchain packages

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 LangChain Dependencies Fix Script${NC}"
echo -e "${BLUE}====================================${NC}"

# Check if we're in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}⚡ Activating virtual environment...${NC}"
    if [ -d ".newvenv" ]; then
        source .newvenv/bin/activate
    elif [ -d "venv" ]; then
        source venv/bin/activate
    else
        echo -e "${RED}❌ No virtual environment found. Please create one first.${NC}"
        exit 1
    fi
fi

echo -e "${YELLOW}📦 Current LangChain packages:${NC}"
pip list | grep -i langchain || echo "None found"

echo -e "\n${BLUE}🔄 Fixing LangChain dependency conflicts...${NC}"

# Uninstall conflicting langchain packages
echo -e "${YELLOW}🗑️  Uninstalling conflicting LangChain packages...${NC}"
pip uninstall -y langchain-anthropic langchain-core langchain-community langchain langchain-openai langchain-google-vertexai langchain-google-community 2>/dev/null || true

# Install compatible versions
echo -e "${YELLOW}📦 Installing compatible LangChain packages...${NC}"

# Install core packages first with compatible versions
pip install langchain-core==0.3.21
pip install langchain-community==0.3.9
pip install langchain==0.3.9
pip install langchain-anthropic==0.2.8
pip install langchain-openai==0.2.10

# Install additional packages that may be needed
pip install langchain-google-vertexai==2.1.1
pip install langchain-google-community==2.1.0

# Install MCP adapters if needed
pip install langchain-mcp-adapters>=0.1.7

echo -e "\n${GREEN}✅ LangChain dependencies fixed!${NC}"

echo -e "\n${YELLOW}📦 Updated LangChain packages:${NC}"
pip list | grep -i langchain

echo -e "\n${BLUE}🚀 Ready to restart Neuro SAN Studio!${NC}"
echo -e "${YELLOW}Run: ./start_neuro_san.sh${NC}"
