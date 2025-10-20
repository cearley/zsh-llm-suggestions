# Contributing to zsh-llm-suggestions

Thank you for your interest in contributing to zsh-llm-suggestions! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Development Setup](#development-setup)
- [Testing](#testing)
- [Making Changes](#making-changes)
- [Submitting Changes](#submitting-changes)
- [Code Style](#code-style)

## Development Setup

### Prerequisites

- **zsh shell** (for testing the plugin functionality)
- **Python 3.8+** (managed via uv or system installation)
- **uv** (recommended) - Install from https://docs.astral.sh/uv/

### Setup Instructions

#### Using uv (Recommended)

1. **Clone and setup:**
   ```bash
   git clone https://github.com/cearley/zsh-llm-suggestions.git
   cd zsh-llm-suggestions
   ```

2. **Initialize development environment:**
   ```bash
   uv sync --dev  # Creates .venv with openai + pygments
   ```

3. **Set up API keys:**
   ```bash
   # Option A: Export in your shell
   export OPENAI_API_KEY="your_openai_api_key_here"

   # Option B: Create .env file (excluded from git)
   cp .env.example .env
   # Edit .env and set OPENAI_API_KEY=your_actual_api_key
   ```

#### Using System Python

If you prefer system-wide installation:

```bash
pip3 install openai
pip3 install pygments  # optional, for syntax highlighting
export OPENAI_API_KEY="your_openai_api_key_here"
```

### Project Structure

```
zsh-llm-suggestions/
├── .venv/                           # uv-managed virtual environment (auto-created)
├── pyproject.toml                   # Project configuration and dependencies
├── uv.lock                          # Dependency lockfile (auto-generated)
├── zsh-llm-suggestions.zsh          # Main plugin file
├── src/
│   └── zsh_llm_suggestions/
│       ├── __init__.py              # Package initialization
│       ├── openai_backend.py        # OpenAI backend
│       ├── copilot_backend.py       # GitHub Copilot backend
│       ├── installer.py             # Interactive installer commands
│       └── data/
│           └── zsh-llm-suggestions.zsh  # Zsh script for installer
├── tests/
│   ├── test_openai_unit.py         # Unit tests
│   └── test_openai_integration.py  # Integration tests
├── test-environment.sh              # Comprehensive manual testing
└── .env                             # API keys (create from .env.example)
```

## Testing

### Automated Tests

This project includes both unit and integration tests.

**Prerequisites:**
- For unit tests: no API key required
- For integration tests: set OPENAI_API_KEY or create a .env file from .env.example
- Optional: set ZSH_LLM_DISABLE_PYGMENTS=1 to disable ANSI formatting during tests

**Quick start with uv:**
```bash
uv run pytest -q          # run unit + integration tests (integration auto-skips without API key)
uv run pytest -q -k unit  # run only unit tests
uv run pytest -q -k integration  # run only integration tests

# Skip integration tests explicitly
SKIP_INTEGRATION_TESTS=1 uv run pytest -q

# Generate coverage HTML report
uv run pytest --cov=. --cov-report=html
open htmlcov/index.html
```

**Using system Python:**
```bash
python3 -m pip install -r requirements-dev.txt  # if available, or install pytest, coverage
python3 -m pytest -q
```

**Test files:**
- `tests/test_openai_unit.py` - Fast unit tests for parsing, error handling, and highlighting
- `tests/test_openai_integration.py` - Real API calls to OpenAI; auto-skipped without OPENAI_API_KEY or if SKIP_INTEGRATION_TESTS=1

### Manual Testing

The project includes a comprehensive manual testing environment for validating functionality before deployment.

**Setup:**

1. **Set up your OpenAI API key** (choose one option):

   Option A - Use existing environment variable:
   ```bash
   # If you already have OPENAI_API_KEY exported in your shell, you're ready to go
   ```

   Option B - Use .env file:
   ```bash
   cp .env.example .env
   # Edit .env and set OPENAI_API_KEY=your_actual_api_key
   ```

2. **Install dependencies** (if not already done):
   ```bash
   uv sync --dev  # or pip3 install openai pygments
   ```

3. **Launch test environment:**
   ```bash
   ./test-environment.sh  # Auto-detects uv or falls back to system python
   ```

**Test Environment Features:**
- Isolated zsh session with all key bindings pre-configured
- Environment variable management via `.env` file
- Dependency validation
- Pre-configured key bindings exactly as documented
- Direct testing aliases for bypassing zsh integration when debugging
- Automatic cleanup of temporary files when session ends

**Available Test Commands:**

Once in the test environment, try these key combinations:

| Key Binding | Function | Example |
|-------------|----------|---------|
| `Ctrl + O` | OpenAI command suggestions | Type "list files recursively" then press Ctrl+O |
| `Ctrl + Alt + O` | OpenAI command explanations | Type "find . -name '*.py'" then press Ctrl+Alt+O |
| `Ctrl + P` | GitHub Copilot suggestions | Type "compress all log files" then press Ctrl+P |
| `Ctrl + Alt + P` | GitHub Copilot explanations | Type "tar -czf logs.tar.gz *.log" then press Ctrl+Alt+P |

**Testing Aliases:**
```bash
test-openai-direct     # Test OpenAI API directly (bypasses zsh integration)
test-openai-explain    # Test OpenAI explanation directly
```

**Example Test Scenarios:**
- **File operations**: "find all python files modified today"
- **System monitoring**: "show memory usage and top processes"
- **Archive management**: "extract all zip files in current directory"
- **Permission management**: "make all shell scripts executable"
- **Network diagnostics**: "check if port 8080 is open"

**Exit Test Environment:**
- Press `Ctrl + D` or type `exit` to return to your normal shell
- All temporary files are automatically cleaned up on exit

### Local CI Testing with act

Test GitHub Actions workflows locally before pushing:

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

## Making Changes

### Branch Strategy

1. **Fork the repository** on GitHub
2. **Create feature branch:** `git checkout -b feature/your-feature-name`
3. **Setup development environment:** `uv sync --dev`

### Development Workflow

4. **Make changes** to the appropriate files:
   - Python backends: `src/zsh_llm_suggestions/`
   - Zsh integration: `zsh-llm-suggestions.zsh`
   - Tests: `tests/`
   - Documentation: `README.md`, `SECURITY_AUDIT.md`, etc.

5. **Run tests:** `uv run pytest` to ensure everything passes
6. **Test manually:** `./test-environment.sh` for interactive testing
7. **Run CI locally:** `act --container-architecture linux/amd64` (requires act)

## Submitting Changes

### Commit Guidelines

- Follow conventional commit format
- Write clear, descriptive commit messages
- Reference issues when applicable

### Pull Request Process

1. **Commit and push:** Push your changes to your fork
2. **Create pull request:** Go to the original repository
3. **Provide description:**
   - Describe the changes and their purpose
   - Reference any related issues
   - Include testing performed
   - Note any breaking changes

### Pull Request Checklist

- [ ] All tests pass
- [ ] New tests added for new functionality
- [ ] Documentation updated (README, CLAUDE.md, etc.)
- [ ] Commit messages follow conventional format
- [ ] No merge conflicts with master branch
- [ ] Manual testing completed

## Code Style

### Python Code

- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to public functions
- Keep functions focused and concise

### Shell Scripts

- Quote all variable expansions
- Use meaningful variable names
- Add comments for complex logic
- Follow existing code patterns

### Documentation

- Use clear, concise language
- Include code examples where appropriate
- Keep formatting consistent
- Update table of contents when adding sections

## Questions or Issues?

- **Bug reports:** Open an issue on GitHub with detailed reproduction steps
- **Feature requests:** Open an issue describing the proposed feature and use case
- **Security vulnerabilities:** See [SECURITY_AUDIT.md](SECURITY_AUDIT.md) for reporting process
- **General questions:** Open a discussion on GitHub

## Additional Resources

- [README.md](README.md) - User-facing documentation
- [RELEASING.md](RELEASING.md) - Release process for maintainers
- [SECURITY_AUDIT.md](SECURITY_AUDIT.md) - Security audit and remediation details
- [CLAUDE.md](CLAUDE.md) - AI-assisted development guidelines

Thank you for contributing to zsh-llm-suggestions!
