# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Project Attribution and Evolution

This codebase began as a fork of [zsh-llm-suggestions](https://github.com/stefanheule/zsh-llm-suggestions). It has since been extensively modernized and restructured, with most files rewritten or heavily modified. The core functionality, architecture, and user experience have diverged significantly from the original.

**Attribution:**
The original author is credited, and the upstream license is retained. See `LICENSE` for details.

**Current Maintainer:**
This project is now actively maintained and developed as a distinct codebase.

## Project Overview

This is `zsh-llm-suggestions`, a zsh plugin that provides LLM-powered command suggestions and explanations directly in the terminal. Users type English descriptions and get shell commands suggested by OpenAI GPT-4 or GitHub Copilot.

## Architecture

The project uses a plugin architecture with fully typed Python 3.9+ code:

1. **Main zsh script**: Core shell integration with functions for handling user input, displaying spinner animations, and managing the query/response flow
   - Source file: `src/zsh_llm_suggestions/data/zsh-llm-suggestions.zsh`
   - Symlink at root: `zsh-llm-suggestions.zsh` → `src/zsh_llm_suggestions/data/zsh-llm-suggestions.zsh`

2. **Plugin Architecture** (Python):
   - **Base module** (`src/zsh_llm_suggestions/base.py`): Shared utilities and abstract base class
     - `LLMBackend` ABC defining the plugin interface
     - `validate_input()`: Input sanitization and security validation
     - `highlight_explanation()`: Syntax highlighting for explanations
   - **Backend implementations** (`src/zsh_llm_suggestions/backends/`):
     - `openai.py`: OpenAIBackend using GPT-4-1106-preview via OpenAI Python SDK
     - `copilot.py`: CopilotBackend using `gh copilot` CLI commands
     - `__init__.py`: Backend registry
   - **Entry points** (thin wrappers, ~20 lines each):
     - `openai_backend.py`: CLI entry point for OpenAI backend
     - `copilot_backend.py`: CLI entry point for Copilot backend
   - **Installer** (`installer.py`): Interactive installation with atomic file operations and safety features

3. **Demo files** (`demo/`): Example interactions showing the plugin in action

## Core Workflow

1. User types English description on zsh command line
2. User presses configured hotkey (e.g., Ctrl+O for OpenAI, Ctrl+P for GitHub Copilot)
3. zsh script spawns Python backend process in background
4. Spinner animation shows while waiting for LLM response
5. Original query gets added to shell history
6. Command line buffer replaced with suggested command
7. For explanations (Ctrl+X then O/P), output is displayed below prompt instead

## Prerequisites and Setup

### Python Version
- **Minimum**: Python 3.9+
- **Rationale**: Modern type annotation syntax (`tuple[...]`, `list[...]` instead of `Tuple`, `List`)

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

## Code Quality Standards

The project follows modern Python development practices:

### Type Safety
- **Full type annotations** on all functions and methods (Python 3.9+ syntax)
- **mypy strict mode enabled** - enforces strictest type checking rules
- **mypy verification** required for all code changes (zero errors policy)
- Built-in types (`tuple`, `list`, `dict`) instead of `typing.Tuple`, `typing.List`, `typing.Dict`
- `TYPE_CHECKING` guards for conditional imports to avoid runtime overhead
- `Optional[T]` for nullable types, `cast()` for type assertions when needed
- All functions have explicit return type annotations (including `-> None`)

### Code Quality
- **Pre-commit hooks** automatically enforcing quality standards before commits
- **Ruff linter** enforcing:
  - pycodestyle (PEP 8)
  - pyflakes (code analysis)
  - isort (import sorting)
  - flake8-bugbear (common bugs)
  - flake8-comprehensions (list/dict comprehensions)
  - pyupgrade (modern Python syntax)
  - flake8-simplify (code simplification)
  - flake8-use-pathlib (prefer pathlib over os.path)
  - flake8-return (return statement best practices)
  - flake8-datetimez (enforce timezone-aware datetimes)
  - flake8-pie (miscellaneous lints)
  - flake8-print (flag print statements in non-CLI code)
- **pytest-randomly** randomizing test execution to catch test interdependencies
- **Package hash verification** for security (uv.lock with hashes)
- **100-character line length** for readability
- **No bare `except` clauses** - always specify exception types
- **Exception chaining** with `from e` or `from None` for proper error context
- **Timezone-aware datetimes** using `datetime.now(timezone.utc)`
- **pathlib for all file operations** instead of os.path

### Plugin Architecture Benefits
- **Extensibility**: Easy to add new LLM backends (Claude, Gemini, Ollama, etc.)
- **Maintainability**: Shared code in `base.py` eliminates duplication (236 lines saved)
- **Type Safety**: Abstract base class ensures all backends implement required methods
- **Testing**: Backend classes can be imported and tested directly without subprocess overhead

See `.serena/memories/modern_python_practices_implementation.md` for complete implementation details.

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
- `ZSH_LLM_LOG_LEVEL`: set logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`; default: `WARNING`)

### GitHub Actions CI
The project includes multiple GitHub Actions workflows:

**CI Workflow** (`.github/workflows/ci.yml`):
- Python script syntax validation
- Error handling verification
- Zsh script sourcing and function definition checks
- Dependency availability tests

**Auto-Release Workflow** (`.github/workflows/auto-release.yml`):
- Triggers after CI succeeds on master
- Automatically creates releases when version changes

**Manual Release Workflow** (`.github/workflows/manual-release.yml`):
- Manually triggered via workflow dispatch
- Backup method for release creation

### Local Workflow Testing with Act
To test GitHub Actions workflows locally before pushing, use [act](https://github.com/nektos/act):

```bash
# Install act (if not already installed)
# See https://nektosact.com/ for installation instructions

# Run all workflows locally (use linux/amd64 for Apple Silicon compatibility)
act --container-architecture linux/amd64

# Run specific workflow
act --container-architecture linux/amd64 -W .github/workflows/ci.yml
act --container-architecture linux/amd64 -W .github/workflows/auto-release.yml

# Run specific job
act --container-architecture linux/amd64 -j test

# List available workflows
act -l

# Quiet mode (reduce noise)
act --container-architecture linux/amd64 -q
```

### Manual Testing
The project includes a comprehensive manual testing environment:

```bash
./test-environment.sh  # Automatically detects uv or system python
```

This creates an isolated zsh session with:
- Pre-configured key bindings (Ctrl+O, Ctrl+P for suggestions; Ctrl+X then O/P for explanations)
- Environment variable management via `.env` file
- Direct testing aliases for debugging
- Automatic dependency validation
- Clean temporary session that doesn't affect your main shell configuration

## Key Implementation Details

### Core Functionality
- Uses temporary files (`/tmp/zsh-llm-suggestions-result`) to communicate between zsh and Python processes
- Implements custom spinner animation while waiting for LLM responses
- Handles edge cases like empty prompts, missing prerequisites, and API errors
- Supports regenerating suggestions by pressing hotkey again when current buffer matches last result

### Plugin Architecture
- **Abstract Base Class**: `LLMBackend` defines the plugin interface with type-safe methods:
  - `check_prerequisites() -> tuple[bool, str]`: Validate backend requirements
  - `generate(prompt: str) -> str`: Generate commands from natural language
  - `explain(command: str) -> str`: Explain what a command does
  - `run(mode: str) -> None`: Main entry point with validation and error handling
- **Input Validation**: All user input sanitized via `validate_input()` (null bytes, length limits, control characters)
- **Type Safety**: Full type annotations throughout codebase, verified with mypy
- **Code Quality**: Linted with Ruff (pycodestyle, pyflakes, isort, bugbear, comprehensions, pyupgrade)
- **Structured Logging**: Comprehensive logging system for debugging and monitoring:
  - Environment variable `ZSH_LLM_LOG_LEVEL` controls verbosity (DEBUG, INFO, WARNING, ERROR)
  - Default level: WARNING (quiet operation, only errors/warnings shown)
  - DEBUG level: Shows all backend operations, API calls, input validation, etc.
  - INFO level: Shows major operations (backend execution, prerequisite checks)
  - User-facing output (installer, status) remains as print() statements
  - Backend errors logged with full stack traces via `exc_info=True`

### Backend Implementations
- **OpenAI backend**:
  - Strips markdown code blocks from GPT-4 responses
  - Uses `# type: ignore[arg-type]` for OpenAI SDK message parameters
  - Null-safe: Asserts client initialization and checks response content
- **Copilot backend**:
  - Uses complex regex patterns to parse `gh copilot` CLI output
  - Subprocess-based with timeout protection (30s)
- **Installer**:
  - Atomic file writes using temp files + `os.replace()`
  - Timestamped backups before modifications
  - Block markers (BEGIN/END) for reliable insertion/removal
  - Interactive prompts via questionary

## Release Management

### Version Configuration
The project uses **dynamic version management** with a single source of truth:
- Version is defined ONLY in `src/zsh_llm_suggestions/__init__.py` as `__version__ = "X.Y.Z"`
- `pyproject.toml` uses `dynamic = ["version"]` to read from `__init__.py`
- Never hardcode version in `pyproject.toml` - it won't work!

### Automated Release Workflow
The project includes automated GitHub release creation:

**Auto-Release** (`.github/workflows/auto-release.yml`):
- Triggers automatically after CI workflow succeeds on master
- Compares current version in `__init__.py` with latest git tag
- If version changed: creates tag and GitHub release with auto-generated notes
- Includes commit history in release notes
- Smart behavior: If CI fails after version bump, just fix and push again - release triggers once CI passes

**Manual Release** (`.github/workflows/manual-release.yml`):
- Backup method via GitHub Actions workflow dispatch
- Allows manual version input and optional `__init__.py` update
- Useful for hotfixes or when auto-release fails

### Release Process
1. Update `__version__` in `src/zsh_llm_suggestions/__init__.py`
2. Commit and push to master
3. CI runs automatically
4. If CI passes: Auto-release creates tag and GitHub release
5. If CI fails: Fix code and push again (no need to re-bump version)

See `RELEASING.md` for complete documentation on release workflows, troubleshooting, and semantic versioning guidelines.

## File Structure

```
zsh-llm-suggestions/
├── .venv/                           # uv-managed virtual environment (auto-created)
├── .pre-commit-config.yaml          # Pre-commit hooks configuration
├── pyproject.toml                   # Project configuration (dynamic version, Ruff/mypy config)
├── uv.lock                          # Dependency lockfile with hashes (auto-generated)
├── zsh-llm-suggestions.zsh          # Symlink to src/zsh_llm_suggestions/data/zsh-llm-suggestions.zsh
├── src/
│   └── zsh_llm_suggestions/
│       ├── __init__.py              # Package metadata with __version__ (single source of truth)
│       ├── base.py                  # Shared utilities and LLMBackend ABC (fully typed)
│       ├── backends/                # Backend implementations (plugin architecture)
│       │   ├── __init__.py          # Backend registry
│       │   ├── openai.py            # OpenAIBackend implementation (fully typed)
│       │   └── copilot.py           # CopilotBackend implementation (fully typed)
│       ├── openai_backend.py        # OpenAI entry point (thin wrapper, ~20 lines)
│       ├── copilot_backend.py       # Copilot entry point (thin wrapper, ~20 lines)
│       ├── installer.py             # Interactive installer with atomic operations
│       └── data/
│           └── zsh-llm-suggestions.zsh  # Main zsh script (source file)
├── .github/
│   └── workflows/
│       ├── ci.yml                   # CI workflow (runs tests)
│       ├── auto-release.yml         # Automated release after CI success
│       └── manual-release.yml       # Manual release workflow dispatch
├── test-environment.sh              # Comprehensive manual testing environment
├── tests/                           # Unit and integration tests
│   ├── conftest.py                  # Test configuration (importlib preload)
│   ├── test_openai_unit.py          # Unit tests (no API key required)
│   └── test_openai_integration.py   # Integration tests (requires API key)
├── .env                             # API keys and environment variables (create from .env.example)
├── .env.example                     # Environment variable template
├── demo/                            # Example usage demonstrations
├── CLAUDE.md                        # AI development documentation (this file)
├── RELEASING.md                     # Release process and workflow documentation
├── SECURITY_AUDIT.md                # Security vulnerability assessment
└── README.md                        # Installation and usage instructions
```

### Development Workflow Commands

**Setup:**
- `uv sync --dev` - Install all dependencies including dev tools (ruff, mypy, pytest, pre-commit)
- `uv run pre-commit install` - Install pre-commit hooks (recommended, runs checks automatically)

**Pre-commit Hooks (Automated):**
- `pre-commit run --all-files` - Manually run all pre-commit hooks
- Pre-commit automatically runs on `git commit`:
  - Ruff linting and formatting
  - mypy type checking
  - Unit tests (integration tests skipped)
  - File quality checks (trailing whitespace, EOF, YAML/TOML syntax)

**Type Checking & Linting (Manual):**
- `uv run mypy src/zsh_llm_suggestions` - Run type checking (must pass with no errors)
- `uv run ruff check src/` - Run linter
- `uv run ruff check --fix src/` - Auto-fix linting issues
- `uv run ruff format src/` - Format code

**Testing:**
- `uv run pytest -v` - Run all tests (integration auto-skipped without API key, randomized order)
- `SKIP_INTEGRATION_TESTS=1 uv run pytest -v` - Force skip integration tests
- `uv run pytest -q -k unit` - Run only unit tests (fast)
- `uv run pytest -q -k integration` - Run only integration tests (requires OPENAI_API_KEY)
- `uv run pytest --cov=. --cov-report=html` - Generate coverage report
- `uv run pytest -p no:randomly` - Disable test randomization if needed
- `./test-environment.sh` - Manual testing in isolated zsh session
- `act --container-architecture linux/amd64` - Test GitHub Actions workflows locally

**Release:**
- Update version: Edit `__version__` in `src/zsh_llm_suggestions/__init__.py`
- Auto-release: Commit version change and push to master (release triggers after CI passes)
- Manual release: Use GitHub Actions workflow dispatch for `.github/workflows/manual-release.yml`
- See `RELEASING.md` for complete release documentation

**Pre-Commit Checklist (if not using hooks):**
1. `uv run mypy src/zsh_llm_suggestions` (must pass)
2. `uv run ruff check src/` (must pass)
3. `SKIP_INTEGRATION_TESTS=1 uv run pytest -v` (all tests pass)

**With pre-commit hooks installed, all checks run automatically on commit!**

**Development Notes:**
- `tests/conftest.py` preloads `importlib` to avoid recursion issues when tests patch `builtins.__import__`
- The OpenAI backend honors `ZSH_LLM_DISABLE_PYGMENTS` to produce deterministic, uncolored output during tests
- The OpenAI backend uses `# type: ignore[arg-type]` for message parameters due to OpenAI SDK's complex TypedDict requirements
- When troubleshooting workflows with `act`, use `-q` flag to reduce output noise
- All Python code must maintain 100% mypy compliance and zero Ruff errors before committing
