#!/usr/bin/env zsh

# Simple test to verify the interactive session issue
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-${(%):-%N}}")" && pwd)"

# Create a minimal test config
TEMP_ZDOTDIR=$(mktemp -d)
TEMP_ZSHRC="$TEMP_ZDOTDIR/.zshrc"
cat > "$TEMP_ZSHRC" << 'EOF'
# Simple test config
export SCRIPT_DIR="/Users/craig/work/zsh-llm-suggestions"

# Test alias
alias test-alias='echo "Alias works! SCRIPT_DIR is: $SCRIPT_DIR"'

# Custom prompt
PS1="%F{yellow}[SIMPLE-TEST]%f %F{blue}%1~%f %# "

echo "=== Simple Test Environment ==="
echo "Try typing: test-alias"
echo "Your prompt should show [SIMPLE-TEST]"
echo "Type 'exit' to return to normal shell"
echo
EOF

# Cleanup function
cleanup() {
    rm -rf "$TEMP_ZDOTDIR"
}
trap cleanup EXIT INT TERM

echo "Starting simple test session..."
ZDOTDIR="$TEMP_ZDOTDIR" exec zsh
