#!/usr/bin/env zsh

# Test Environment for zsh-llm-suggestions
# This script creates a temporary zsh environment for manual testing

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-${(%):-%N}}")" && pwd)"

echo -e "${BLUE}🧪 zsh-llm-suggestions Test Environment${NC}"
echo -e "${BLUE}======================================${NC}\n"

# Check for existing OPENAI_API_KEY in environment
echo -e "${BLUE}📦 Loading environment variables...${NC}"
ENV_FILE="$SCRIPT_DIR/.env"

# First check if OPENAI_API_KEY is already set in the current environment
if [[ -n "$OPENAI_API_KEY" && "$OPENAI_API_KEY" != "your_openai_api_key_here" ]]; then
    echo -e "   ${GREEN}✅ Found OPENAI_API_KEY in shell environment${NC}"
    ENV_SOURCE="shell environment"
else
    # Check if .env file exists
    if [[ ! -f "$ENV_FILE" ]]; then
        echo -e "${YELLOW}⚠️  Creating .env file template...${NC}"
        cat > "$ENV_FILE" << 'EOF'
# Environment variables for testing zsh-llm-suggestions
# Copy this file and set your actual API key

# Required for OpenAI functionality
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Uncomment to test with different model
# OPENAI_MODEL=gpt-4-1106-preview
EOF
        echo -e "${RED}❌ OPENAI_API_KEY not found in environment${NC}"
        echo -e "   Please edit $ENV_FILE and set your OPENAI_API_KEY, or export it in your shell.\n"
        exit 1
    fi

    # Source .env file and validate
    source "$ENV_FILE"

    if [[ -z "$OPENAI_API_KEY" || "$OPENAI_API_KEY" == "your_openai_api_key_here" ]]; then
        echo -e "${RED}❌ OPENAI_API_KEY not properly set in $ENV_FILE${NC}"
        echo -e "   Please edit the .env file and set your actual API key, or export it in your shell.\n"
        exit 1
    fi

    echo -e "   ${GREEN}✅ Found OPENAI_API_KEY in .env file${NC}"
    ENV_SOURCE=".env file"
fi

# Check dependencies
echo -e "${BLUE}🔍 Checking dependencies...${NC}"

# Check if uv is available and prefer it
if command -v uv &> /dev/null; then
    echo -e "   ${GREEN}✅ uv found - using isolated environment${NC}"
    UV_AVAILABLE=true

    # Initialize uv project if .venv doesn't exist
    if [[ ! -d "$SCRIPT_DIR/.venv" ]]; then
        echo -e "${BLUE}🔧 Initializing uv environment...${NC}"
        cd "$SCRIPT_DIR"
        uv sync --dev
        cd - > /dev/null
    fi

    # Check if dependencies are available in uv environment
    if ! uv run python -c "import openai" &> /dev/null; then
        echo -e "${RED}❌ openai not available in uv environment${NC}"
        echo -e "   Run: uv sync"
        exit 1
    fi

    # Check pygments in uv environment
    if uv run python -c "import pygments" &> /dev/null; then
        PYGMENTS_STATUS="${GREEN}✅ installed in uv environment${NC}"
    else
        PYGMENTS_STATUS="${YELLOW}⚠️  not installed in uv environment (explanations won't be highlighted)${NC}"
    fi

    PYTHON_CMD="uv run python"
    echo -e "   python (uv): ${GREEN}✅ found${NC}"
    echo -e "   openai (uv): ${GREEN}✅ installed${NC}"
    echo -e "   pygments (uv): $PYGMENTS_STATUS"
else
    echo -e "${BLUE}📦 uv not found, using system python...${NC}"
    UV_AVAILABLE=false

    # Check python3
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ python3 not found${NC}"
        exit 1
    fi

    # Check openai package
    if ! python3 -c "import openai" &> /dev/null; then
        echo -e "${RED}❌ openai package not installed${NC}"
        echo -e "   Run: pip3 install openai"
        echo -e "   Or install uv and run: uv sync"
        exit 1
    fi

    # Check pygments (optional)
    if python3 -c "import pygments" &> /dev/null; then
        PYGMENTS_STATUS="${GREEN}✅ installed${NC}"
    else
        PYGMENTS_STATUS="${YELLOW}⚠️  not installed (explanations won't be highlighted)${NC}"
    fi

    PYTHON_CMD="python3"
    echo -e "   python3: ${GREEN}✅ found${NC}"
    echo -e "   openai: ${GREEN}✅ installed${NC}"
    echo -e "   pygments: $PYGMENTS_STATUS"
fi

# Check GitHub CLI (for copilot functionality)
if command -v gh &> /dev/null; then
    GH_STATUS="${GREEN}✅ installed${NC}"
    if gh extension list | grep -q "github/gh-copilot"; then
        COPILOT_STATUS="${GREEN}✅ installed${NC}"
    else
        COPILOT_STATUS="${YELLOW}⚠️  not installed${NC}"
    fi
else
    GH_STATUS="${YELLOW}⚠️  not installed${NC}"
    COPILOT_STATUS="${YELLOW}⚠️  gh cli required${NC}"
fi

echo -e "   gh cli: $GH_STATUS"
echo -e "   gh copilot: $COPILOT_STATUS"
echo

# Create temporary zsh configuration directory
TEMP_ZDOTDIR=$(mktemp -d)
TEMP_ZSHRC="$TEMP_ZDOTDIR/.zshrc"
echo -e "${BLUE}📝 Creating temporary zsh configuration...${NC}"

cat > "$TEMP_ZSHRC" << EOF
# Temporary zsh configuration for testing zsh-llm-suggestions
# This file will be automatically deleted when the test session ends

# Load the plugin
source "$SCRIPT_DIR/zsh-llm-suggestions.zsh"

# Set up key bindings (as documented in README.md)
bindkey '^o' zsh_llm_suggestions_openai              # Ctrl+O for OpenAI suggestions
bindkey '^xo' zsh_llm_suggestions_openai_explain     # Ctrl+X then O for OpenAI explanations
bindkey '^p' zsh_llm_suggestions_github_copilot      # Ctrl+P for GitHub Copilot suggestions
bindkey '^xp' zsh_llm_suggestions_github_copilot_explain # Ctrl+X then P for GitHub Copilot explanations

# Set up environment variables
export OPENAI_API_KEY="$OPENAI_API_KEY"

# Force ASCII spinner for test environment (better compatibility)
# Users can change this to "unicode" if their terminal/font supports Braille characters
export ZSH_LLM_SPINNER_STYLE="ascii"

# Export variables for use in aliases
export SCRIPT_DIR="${SCRIPT_DIR}"

# Helpful aliases for testing (using proper command execution)
if [[ "$UV_AVAILABLE" == "true" ]]; then
    alias test-openai-direct='echo "list files in current directory" | uv run python "\$SCRIPT_DIR/src/zsh_llm_suggestions/openai_backend.py" generate'
    alias test-openai-explain='echo "ls -la" | uv run python "\$SCRIPT_DIR/src/zsh_llm_suggestions/openai_backend.py" explain'
else
    alias test-openai-direct='echo "list files in current directory" | python3 "\$SCRIPT_DIR/src/zsh_llm_suggestions/openai_backend.py" generate'
    alias test-openai-explain='echo "ls -la" | python3 "\$SCRIPT_DIR/src/zsh_llm_suggestions/openai_backend.py" explain'
fi

# Custom prompt to indicate test mode
PS1="%F{yellow}[TEST]%f %F{blue}%1~%f %# "

# Show instructions on startup
cat << 'INSTRUCTIONS'

🧪 zsh-llm-suggestions Test Environment Active
===============================================

Spinner Mode: ASCII (|/-\) for maximum compatibility
  To test Unicode spinner: export ZSH_LLM_SPINNER_STYLE="unicode"
  To revert to ASCII: export ZSH_LLM_SPINNER_STYLE="ascii"

Available Key Bindings:
  Ctrl+O        : OpenAI command suggestions
  Ctrl+X then O : OpenAI command explanations
  Ctrl+P        : GitHub Copilot suggestions (if available)
  Ctrl+X then P : GitHub Copilot explanations (if available)

Test Aliases:
  test-openai-direct  : Test OpenAI API directly (bypasses zsh integration)
  test-openai-explain : Test OpenAI explanation directly

Usage Instructions:
1. Type a description like: "find all python files"
2. Press Ctrl+O to get OpenAI suggestion
3. If you get a command, press Ctrl+X then O to get explanation
4. Type 'exit' to leave test environment

Example Commands to Try:
  - "list all files recursively"
  - "find files modified in last 7 days"
  - "count lines in all python files"
  - "compress all log files"

INSTRUCTIONS

EOF

# Cleanup function
cleanup() {
    echo -e "\n${BLUE}🧹 Cleaning up temporary files...${NC}"
    rm -rf "$TEMP_ZDOTDIR"
    echo -e "${GREEN}✅ Test environment cleaned up${NC}"
}

# Set trap for cleanup
trap cleanup EXIT INT TERM

echo -e "${GREEN}✅ Test environment ready!${NC}"
echo -e "${BLUE}🚀 Starting temporary zsh session...${NC}"
echo -e "${YELLOW}   (Press Ctrl+D or type 'exit' to return)${NC}\n"

# Start the test zsh session
ZDOTDIR="$TEMP_ZDOTDIR" exec zsh
