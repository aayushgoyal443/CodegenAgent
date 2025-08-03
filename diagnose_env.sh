#!/bin/bash

# Environment Diagnostic Script
# Helps diagnose Python environment and dependency issues

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Neuro SAN Environment Diagnostic${NC}"
echo -e "${BLUE}===================================${NC}"

# Check current working directory
echo -e "\n${YELLOW}📂 Current Directory:${NC}"
pwd

# Check Python versions
echo -e "\n${YELLOW}🐍 Python Information:${NC}"
echo -e "System Python: $(which python3)"
echo -e "Python Version: $(python3 --version)"

# Check virtual environment
echo -e "\n${YELLOW}🏠 Virtual Environment:${NC}"
if [ -n "$VIRTUAL_ENV" ]; then
    echo -e "${GREEN}✅ Virtual environment active: $VIRTUAL_ENV${NC}"
    echo -e "Virtual env Python: $(which python)"
else
    echo -e "${RED}❌ No virtual environment active${NC}"

    # Try to find and activate virtual environment
    if [ -d ".newvenv" ]; then
        echo -e "${YELLOW}Found .newvenv, attempting to activate...${NC}"
        source .newvenv/bin/activate
        echo -e "After activation - VIRTUAL_ENV: $VIRTUAL_ENV"
    elif [ -d "venv" ]; then
        echo -e "${YELLOW}Found venv, attempting to activate...${NC}"
        source venv/bin/activate
        echo -e "After activation - VIRTUAL_ENV: $VIRTUAL_ENV"
    fi
fi

# Check installed packages
echo -e "\n${YELLOW}📦 LangChain Package Status:${NC}"

packages=(
    "langchain_anthropic"
    "langchain_core"
    "langchain_openai"
    "langchain_community"
    "langchain"
)

for package in "${packages[@]}"; do
    echo -n "  $package: "
    if python -c "import $package" 2>/dev/null; then
        # Get version if possible
        version=$(python -c "import $package; print(getattr($package, '__version__', 'unknown'))" 2>/dev/null)
        echo -e "${GREEN}✅ installed (v$version)${NC}"
    else
        echo -e "${RED}❌ missing${NC}"
    fi
done

# Check pip list for langchain packages
echo -e "\n${YELLOW}📋 All LangChain packages (pip list):${NC}"
pip list | grep -i langchain || echo -e "${RED}No langchain packages found${NC}"

# Check neuro-san installation
echo -e "\n${YELLOW}🧠 Neuro SAN Package:${NC}"
if python -c "import neuro_san" 2>/dev/null; then
    version=$(python -c "import neuro_san; print(getattr(neuro_san, '__version__', 'unknown'))" 2>/dev/null)
    echo -e "${GREEN}✅ neuro-san installed (v$version)${NC}"
else
    echo -e "${RED}❌ neuro-san not found${NC}"
fi

# Check requirements.txt
echo -e "\n${YELLOW}📄 Requirements file:${NC}"
if [ -f "requirements.txt" ]; then
    echo -e "${GREEN}✅ requirements.txt exists${NC}"
    echo -e "Contents:"
    cat requirements.txt | head -10
else
    echo -e "${RED}❌ requirements.txt not found${NC}"
fi

# Check .env file
echo -e "\n${YELLOW}🔧 Environment file:${NC}"
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ .env exists${NC}"
    if grep -q "ANTHROPIC_API_KEY" .env; then
        echo -e "${GREEN}✅ ANTHROPIC_API_KEY found in .env${NC}"
    else
        echo -e "${RED}❌ ANTHROPIC_API_KEY not found in .env${NC}"
    fi
else
    echo -e "${RED}❌ .env not found${NC}"
fi

# Test langchain_anthropic import specifically
echo -e "\n${YELLOW}🧪 Testing langchain_anthropic import:${NC}"
python -c "
try:
    import langchain_anthropic
    from langchain_anthropic.chat_models import ChatAnthropic
    print('✅ langchain_anthropic imports successfully')
except ImportError as e:
    print(f'❌ Import failed: {e}')
except Exception as e:
    print(f'❌ Other error: {e}')
"

echo -e "\n${BLUE}📝 Diagnostic Summary:${NC}"
echo -e "${YELLOW}If langchain_anthropic is missing, try:${NC}"
echo -e "1. Make sure virtual environment is activated"
echo -e "2. Run: pip install langchain-anthropic"
echo -e "3. Or run: ./fix_dependencies.sh"

echo -e "\n${BLUE}🎯 Next Steps:${NC}"
echo -e "Based on the above output, we can determine the issue."
