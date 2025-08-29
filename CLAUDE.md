# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is `zsh-llm-suggestions`, a zsh plugin that provides LLM-powered command suggestions and explanations directly in the terminal. Users type English descriptions and get shell commands suggested by OpenAI GPT-4 or GitHub Copilot.

## Architecture

The project consists of several key components:

1. **Main zsh script** (`zsh-llm-suggestions.zsh`): Core shell integration with functions for handling user input, displaying spinner animations, and managing the query/response flow
2. **LLM backends**: Two Python scripts that interface with different LLM providers:
   - `zsh-llm-suggestions-openai.py`: Uses OpenAI's GPT-4-1106-preview model via the OpenAI Python SDK
   - `zsh-llm-suggestions-github-copilot.py`: Uses GitHub Copilot via the `gh copilot` CLI command
3. **Demo files** (`demo/`): Example interactions showing the plugin in action

## Core Workflow

1. User types English description on zsh command line
2. User presses configured hotkey (e.g., Ctrl+O for OpenAI, Ctrl+P for GitHub Copilot)
3. zsh script spawns Python backend process in background
4. Spinner animation shows while waiting for LLM response
5. Original query gets added to shell history
6. Command line buffer replaced with suggested command
7. For explanations (Ctrl+Alt+O/P), output is displayed below prompt instead

## Prerequisites and Setup

### Development Environment (Recommended: uv)
This project uses `uv` for fast, reliable Python dependency management with isolated environments:

```bash
# Install uv: https://docs.astral.sh/uv/
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup project
uv sync --dev  # Creates .venv with openai + pygments automatically

# Test environment will automatically detect and use uv
./test-environment.sh
```

### OpenAI Backend
- **API Key**: Set `OPENAI_API_KEY` environment variable or create `.env` file
- **Dependencies**: Automatically managed by `uv sync --dev`
  - `openai>=1.0.0` (required)
  - `pygments>=2.10.0` (optional, for syntax-highlighted explanations)

### GitHub Copilot Backend  
- **GitHub CLI**: `gh` command available
- **Authentication**: `gh auth login --web -h github.com`
- **Extension**: `gh extension install github/gh-copilot`

### Legacy Setup (System Python)
If you prefer system-wide installation:
- `pip3 install openai`
- `pip3 install pygments` (optional)
- Export `OPENAI_API_KEY` in your shell

## Testing

### Unit and Integration Tests

- Unit tests live in `tests/test_openai_unit.py` and do not require network or API keys.
- Integration tests live in `tests/test_openai_integration.py` and make real API calls.
- Use `uv run pytest` to run tests; integration tests will be auto-skipped if `OPENAI_API_KEY` is not set or if `SKIP_INTEGRATION_TESTS=1`.
- Coverage HTML output is generated to `htmlcov/` when running with `--cov`.

Example commands:
```bash
uv run pytest -q                       # run all (integration auto-skip w/o key)
SKIP_INTEGRATION_TESTS=1 uv run pytest # force-skip integration
uv run pytest --cov=. --cov-report=html && open htmlcov/index.html
```

Environment variables used by tests:
- `OPENAI_API_KEY`: required for integration tests (can be populated from `.env`)
- `SKIP_INTEGRATION_TESTS`: set to `1|true|yes` to skip integration tests
- `ZSH_LLM_DISABLE_PYGMENTS`: set to `1|true|yes` to disable ANSI formatting for predictable test output

### GitHub Actions CI
The project includes a GitHub Actions workflow (`.github/workflows/ci.yml`) that runs smoke tests including:
- Python script syntax validation
- Error handling verification
- Zsh script sourcing and function definition checks
- Dependency availability tests

### Local Workflow Testing with Act
To test GitHub Actions workflows locally before pushing, use [act](https://github.com/nektos/act):

```bash
# Install act (if not already installed)
# See https://nektosact.com/ for installation instructions

# Run workflows locally (use linux/amd64 for Apple Silicon compatibility)
act --container-architecture linux/amd64

# Run specific workflow
act --container-architecture linux/amd64 -W .github/workflows/ci.yml

# Run specific job
act --container-architecture linux/amd64 -j test

# List available workflows
act -l
```

### Manual Testing
The project includes a comprehensive manual testing environment:

```bash
./test-environment.sh  # Automatically detects uv or system python
```

This creates an isolated zsh session with:
- Pre-configured key bindings (Ctrl+O, Ctrl+P, etc.)
- Environment variable management via `.env` file
- Direct testing aliases for debugging
- Automatic dependency validation
- Clean temporary session that doesn't affect your main shell configuration

## Key Implementation Details

- Uses temporary files (`/tmp/zsh-llm-suggestions-result`) to communicate between zsh and Python processes
- Implements custom spinner animation while waiting for LLM responses
- Handles edge cases like empty prompts, missing prerequisites, and API errors
- Supports regenerating suggestions by pressing hotkey again when current buffer matches last result
- Both backends parse and clean LLM responses to extract just the command or explanation text
- OpenAI backend strips markdown code blocks from responses
- GitHub Copilot backend uses complex regex patterns to parse the `gh copilot` CLI output

## File Structure

```
zsh-llm-suggestions/
├── .venv/                           # uv-managed virtual environment (auto-created)
├── pyproject.toml                   # Project configuration and dependencies  
├── uv.lock                          # Dependency lockfile (auto-generated)
├── zsh-llm-suggestions.zsh          # Main plugin file to be sourced in `.zshrc`
├── zsh-llm-suggestions-openai.py    # OpenAI backend
├── zsh-llm-suggestions-github-copilot.py  # GitHub Copilot backend
├── test-environment.sh              # Comprehensive manual testing environment
├── .env                             # API keys and environment variables (create from .env.example)
├── .env.example                     # Environment variable template
├── demo/                            # Example usage demonstrations
├── CLAUDE.md                        # AI development documentation (this file)
├── SECURITY_AUDIT.md                # Security vulnerability assessment
└── README.md                        # Installation and usage instructions
```

### Development Workflow Commands

- Setup: `uv sync --dev` (creates isolated environment)
- Unit tests: `uv run pytest -q -k unit`
- Integration tests: `uv run pytest -q -k integration` (requires OPENAI_API_KEY)
- Skip integration: `SKIP_INTEGRATION_TESTS=1 uv run pytest -q`
- Coverage: `uv run pytest --cov=. --cov-report=html`
- Manual tests: `./test-environment.sh`
- CI: `act --container-architecture linux/amd64` (local workflow testing)

Notes:
- `tests/conftest.py` preloads `importlib` to avoid recursion issues when tests patch `builtins.__import__`.
- The OpenAI backend honors `ZSH_LLM_DISABLE_PYGMENTS` to produce deterministic, uncolored output during tests.
- When troubleshooting a workflow using `act`, you can cut down the output 'noise' by using the flag -q, --quiet to disable logging of output from steps.