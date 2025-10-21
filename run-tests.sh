#!/usr/bin/env bash

# Test runner script for zsh-llm-suggestions
# This script runs both unit and integration tests

set -e

echo "🧪 zsh-llm-suggestions Test Runner"
echo "=================================="

# Check if uv is available
if command -v uv &> /dev/null; then
    PYTHON_CMD="uv run python"
    PYTEST_CMD="uv run pytest"
    echo "📦 Using uv environment"

    # Install test dependencies if not already installed
    echo "🔧 Installing test dependencies..."
    uv sync --group=test --group=dev
else
    PYTHON_CMD="python3"
    PYTEST_CMD="pytest"
    echo "📦 Using system python"

    # Check if pytest is available
    if ! command -v pytest &> /dev/null; then
        echo "❌ pytest not found. Install with: pip3 install pytest pytest-cov coverage"
        exit 1
    fi
fi

echo

# Run unit tests (no API key required)
echo "🔬 Running unit tests..."
echo "------------------------"
$PYTEST_CMD tests/test_openai_unit.py -m "not integration" -v

echo
echo "📊 Unit test summary:"
echo "- These tests verify core functionality without making API calls"
echo "- They test markdown parsing, error handling, and input validation"
echo

# Check for API key for integration tests
API_KEY=""
if [[ -n "$OPENAI_API_KEY" ]]; then
    API_KEY="$OPENAI_API_KEY"
    SOURCE="environment variable"
elif [[ -f ".env" ]]; then
    # Try to extract from .env file
    API_KEY=$(grep "^OPENAI_API_KEY=" .env | cut -d'=' -f2- | tr -d '"'"'"'')
    SOURCE=".env file"
fi

if [[ -n "$API_KEY" && "$API_KEY" != "your_openai_api_key_here" ]]; then
    echo "🌐 API key found in $SOURCE"
    echo "🚀 Running integration tests (this may take a moment)..."
    echo "----------------------------------------------------------"

    # Export the API key if it came from .env
    if [[ "$SOURCE" == ".env file" ]]; then
        export OPENAI_API_KEY="$API_KEY"
    fi

    $PYTEST_CMD tests/test_openai_integration.py -v

    echo
    echo "📊 Integration test summary:"
    echo "- These tests make real API calls to verify end-to-end functionality"
    echo "- They test markdown parsing with real LLM responses"
    echo "- API usage: Each test makes 1-3 API calls (small cost)"
else
    echo "⚠️  No valid OPENAI_API_KEY found - skipping integration tests"
    echo "   Set your API key or create a .env file to run integration tests"
    echo "   Integration tests verify real API behavior and markdown parsing"
fi

echo
echo "✅ Test run complete!"
echo
echo "Available test commands:"
echo "  $PYTEST_CMD tests/                          # Run all tests"
echo "  $PYTEST_CMD tests/test_openai_unit.py       # Unit tests only"
echo "  $PYTEST_CMD tests/test_openai_integration.py # Integration tests only"
echo "  SKIP_INTEGRATION_TESTS=1 $PYTEST_CMD tests/ # Skip integration tests"
echo
echo "Coverage report available in: htmlcov/index.html"
