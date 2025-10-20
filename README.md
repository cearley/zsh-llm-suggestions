# LLM-based command suggestions for zsh

[![CI](https://github.com/cearley/zsh-llm-suggestions/actions/workflows/ci.yml/badge.svg)](https://github.com/cearley/zsh-llm-suggestions/actions)
[![Maintained](https://img.shields.io/badge/maintained-yes-green.svg)](https://github.com/cearley/zsh-llm-suggestions/graphs/commit-activity)
[![Last Commit](https://img.shields.io/github/last-commit/cearley/zsh-llm-suggestions)](https://github.com/cearley/zsh-llm-suggestions/commits/master)
[![Security](https://img.shields.io/badge/security-major%20vulnerabilities%20resolved-yellow.svg)](SECURITY_AUDIT.md)
[![License](https://img.shields.io/github/license/cearley/zsh-llm-suggestions)](LICENSE)
[![Shell](https://img.shields.io/badge/shell-zsh-blue.svg)](https://www.zsh.org/)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)

## Table of Contents

- [About This Fork](#about-this-fork)
- [Security](#security)
- [Original Documentation](#original-documentation)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Warning](#warning)
- [Supported LLMs](#supported-llms)
- [Development Setup (Fork Enhancement)](#development-setup-fork-enhancement)
- [Automated Tests (Fork Enhancement)](#automated-tests-fork-enhancement)
- [Manual Testing (Fork Enhancement)](#manual-testing-fork-enhancement)
- [Contributing](#contributing)

**For Maintainers:**
- [RELEASING.md](RELEASING.md) - Release process documentation
- [SECURITY_AUDIT.md](SECURITY_AUDIT.md) - Security audit and remediation

---

## About This Fork

**✅ Status: Acceptable for personal and development use** (see [Security](#security) section for details)

This is a maintained fork of [stefanheule/zsh-llm-suggestions](https://github.com/stefanheule/zsh-llm-suggestions), which hasn't been actively maintained. This fork includes several important improvements:

**Recent Enhancements (v0.2.0 - October 2025):**
- ✅ **Major security vulnerabilities resolved** - All 5 critical/high vulnerabilities fixed
- ✅ **Secure temporary file handling** - Unpredictable paths with automatic cleanup
- ✅ **Input validation** - Protection against abuse and malicious payloads
- ✅ **Network timeouts** - 30-second timeouts prevent indefinite hangs
- ✅ **Removed unsafe `eval` usage** - Proper command execution with quoting
- ✅ **Comprehensive test coverage** - 13 unit tests including security-specific tests

**Recent Enhancements (v0.1.0 - October 2025):**
- ✅ **`uv tool install` support** - Install globally with a single command, no git clone required
- ✅ **Interactive installer** - Automated setup with `zsh-llm-install` command
- ✅ **Dual installation methods** - Choose between `uv tool install` or traditional git clone
- ✅ **GitHub Actions CI/CD** with comprehensive smoke tests
- ✅ **Local testing support** with `act` for workflow validation
- ✅ **[Comprehensive security audit](SECURITY_AUDIT.md)** identifying and resolving vulnerabilities
- ✅ **Updated OpenAI library compatibility** (resolved import errors)
- ✅ **Developer documentation** (CLAUDE.md for AI-assisted development)

**Why Choose This Fork:**
- **Security-focused** - All identified vulnerabilities have been remediated
- **Easy installation** with `uv tool install` - no git clone required
- **Active maintenance** with recent commits and ongoing development
- **Modern tooling** including CI/CD, local testing, and comprehensive documentation
- **Dual installation methods** supporting both `uv tool install` and traditional git clone
- **Well-tested** with unit tests, integration tests, and security validation

**Planned Improvements:**
- 🚀 **Architecture improvements** for better reliability and performance
- 🚀 **New features** including configuration management and caching
- 🚀 **Additional LLM backends** (Claude, local models)

**Use Original If:** You prefer the original codebase without recent updates
**Use This Fork If:** You want security fixes, modern tooling, and active maintenance

---

## Original Documentation

![Demo of zsh-llm-suggestions](https://github.com/stefanheule/zsh-llm-suggestions/blob/master/zsh-llm-suggestions.gif?raw=true)

`zsh` commands can be difficult to remember, but LLMs are great at turning
human descriptions of what to do into a command. Enter `zsh-llm-suggestions`:
You describe what you would like to do directly in your prompt, you hit a
keyboard shortcut of your choosing, and the LLM replaces your request with
the command.

Similarly, if you have a command that you don't understand, `zsh-llm-suggestions`
can query an LLM for you to explain that command. You can combine these, by
first generating a command from a human description, and then asking the LLM
to explain the command.

## Quick Start

### Option 1: Install via `uv` (Recommended)

The fastest way to get started:

```bash
# Install globally with uv
uv tool install git+https://github.com/cearley/zsh-llm-suggestions@latest

# Run the interactive installer
zsh-llm-install

# Restart your shell or source your config
source ~/.zshrc
```

### Option 2: Clone Repository (Classic Method)

Traditional installation method:

```bash
# Clone to your preferred location
git clone https://github.com/cearley/zsh-llm-suggestions.git ~/.local/share/zsh-llm-suggestions

# Add to ~/.zshrc
echo 'source ~/.local/share/zsh-llm-suggestions/zsh-llm-suggestions.zsh' >> ~/.zshrc

# Configure key bindings (add to ~/.zshrc)
bindkey '^o' zsh_llm_suggestions_openai              # Ctrl + O for OpenAI suggestions
bindkey '^[^o' zsh_llm_suggestions_openai_explain   # Ctrl + Alt + O for explanations
bindkey '^p' zsh_llm_suggestions_github_copilot     # Ctrl + P for Copilot suggestions
bindkey '^[^p' zsh_llm_suggestions_github_copilot_explain # Ctrl + Alt + P for explanations

# Restart your shell
```

Both methods work identically once set up!

## Installation

### Method 1: Using `uv` (Recommended)

`uv` provides the easiest installation and update experience:

```bash
# Install the tool globally
uv tool install git+https://github.com/cearley/zsh-llm-suggestions@latest
```

This installs five commands:
- `zsh-llm-openai` - OpenAI backend (called by Ctrl+O)
- `zsh-llm-copilot` - GitHub Copilot backend (called by Ctrl+P)
- `zsh-llm-install` - Interactive setup wizard
- `zsh-llm-uninstall` - Remove zsh integration
- `zsh-llm-status` - Check installation status

**Run the interactive installer:**

```bash
zsh-llm-install
```

The installer will:
- Copy the zsh script to `~/.local/share/zsh-llm-suggestions/`
- Offer to add the source line to your `~/.zshrc`
- Configure key bindings automatically

**Updating:**

```bash
# Update to latest version
uv tool upgrade zsh-llm-suggestions
```

**Uninstalling:**

```bash
# Remove zsh integration
zsh-llm-uninstall

# Remove the tool
uv tool uninstall zsh-llm-suggestions
```

### Method 2: Clone Repository

Clone the repository:

```
git clone https://github.com/cearley/zsh-llm-suggestions.git ~/zsh/zsh-llm-suggestions
```

Source the script and configure the hotkey in `.zshrc`:

```
source ~/zsh/zsh-llm-suggestions/zsh-llm-suggestions.zsh
bindkey '^o' zsh_llm_suggestions_openai # Ctrl + O to have OpenAI suggest a command given a English description
bindkey '^[^o' zsh_llm_suggestions_openai_explain # Ctrl + alt + O to have OpenAI explain a command
bindkey '^p' zsh_llm_suggestions_github_copilot # Ctrl + P to have GitHub Copilot suggest a command given a English description
bindkey '^[^p' zsh_llm_suggestions_github_copilot_explain # Ctrl + alt + P to have GitHub Copilot explain a command
```

Make sure `python3` is installed.

Both LLMs require a bit of configuration. Either follow the rest of the instructions
here, or just enter something on the prompt (because an empty prompt won't run the
LLM) and hit your configured keyboard shortcut. Instead of answering the prompt, it will
tell you how to finish the setup.

For `zsh_llm_suggestions_openai` (OpenAI-based suggestions):
- Set the `OPENAI_API_KEY` environment variable to your API key. You can get it
  from [https://platform.openai.com/api-keys](platform.openai.com/api-keys). Note
  that every suggestion costs a small amount of money, you are solely responsible for
  these charges.
  ```
  export OPENAI_API_KEY="..."
  ```
- Install the Python 3 package `openai`:
  ```
  pip3 install openai
  ```
- Optional, if you want syntax highlighting for the command explanation, install pygments
  ```
  pip3 install pygments
  ```

For `zsh_llm_suggestions_github_copilot` (GitHub Copilot suggestions):
- Install GitHub CLI: Follow [https://github.com/cli/cli#installation](github.com/cli/cli#installation).
- Authenticate with GitHub:
  ```
  /usr/bin/gh auth login --web -h github.com
  ```
- Install GitHub Copilot extension:
  ```
  /usr/bin/gh extension install github/gh-copilot
  ```

## Usage

### LLM suggested commands

Type out what you'd like to do in English, then hit ctrl+P or ctrl+O (or whatever hotkey)
you configured. `zsh-llm-suggestions` will then query OpenAI or GitHub Copilot, and replace
the query with the command suggested.

If you don't like the suggestion and think the LLM can do better, just hit ctrl+P/O again,
and a new suggestion will be fetched.

### Explain commands using LLM

If you typed a command (or maybe the LLM generated one) that you don't understand, hit
ctrl+alt+O to have OpenAI explain the command in English, or hit ctrl+alt+P to have
GitHub Copilot explain it.

## Warning

There are some risks using `zsh-llm-suggestions`:
1. LLMs can suggest bad commands, it is up to you to make sure you
   are okay executing the commands.
2. The supported LLMs are not free, so you might incur a cost when using `zsh-llm-suggestions`.

## Supported LLMs

Right now, two LLMs are supported:
1. GitHub Copilot (via GitHub CLI). Requires a GitHub Copilot subscription.
2. OpenAI. Requires an OpenAI API key. Currently uses `gpt-4-1106-preview`.

---

*End of original documentation. Fork-specific additions below:*

## Development Setup (Fork Enhancement)

This fork uses modern Python tooling for development. The recommended setup uses `uv` for fast, reliable dependency management with isolated environments.

### Prerequisites

- **zsh shell** (for testing the plugin functionality)
- **Python 3.8+** (managed via uv or system installation)
- **uv** (recommended) - Install from [https://docs.astral.sh/uv/](https://docs.astral.sh/uv/)

### Recommended Development Workflow

**🚀 Using `uv` (Recommended)**

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

4. **Run tests:**
   ```bash
   ./test-environment.sh  # Automatically detects and uses uv environment
   ```

**📦 Alternative: System Python**

If you prefer system-wide installation:

```bash
pip3 install openai
pip3 install pygments  # optional, for syntax highlighting
export OPENAI_API_KEY="your_openai_api_key_here"
./test-environment.sh
```

### Development Features

- **Isolated environments**: uv creates project-specific `.venv` automatically
- **Fast installs**: uv is significantly faster than pip for dependency resolution
- **Lockfile support**: `uv.lock` ensures reproducible builds
- **Development dependencies**: Includes optional packages like `pygments` for enhanced functionality
- **Automatic detection**: Test scripts automatically detect and use uv when available

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

### Contributing

When contributing to this project:

1. **Fork the repository** on GitHub
2. **Create feature branch:** `git checkout -b feature/your-feature-name`
3. **Setup development environment:** `uv sync --dev`
4. **Make changes** to the appropriate files:
   - Python backends: `src/zsh_llm_suggestions/`
   - Zsh integration: `zsh-llm-suggestions.zsh`
   - Tests: `tests/`
5. **Run tests:** `uv run pytest` to ensure everything passes
6. **Test manually:** `./test-environment.sh` for interactive testing
7. **Run CI locally:** `act --container-architecture linux/amd64` (requires [act](https://github.com/nektos/act))
8. **Commit and push:** Follow conventional commit format
9. **Create pull request:** Include description of changes and testing performed

## Automated Tests (Fork Enhancement)

This fork includes both unit and integration tests. You can run them with uv (recommended) or system Python.

- Prerequisites:
  - For unit tests: no API key required.
  - For integration tests: set OPENAI_API_KEY or create a .env file from .env.example.
  - Optional: set ZSH_LLM_DISABLE_PYGMENTS=1 to disable ANSI formatting during tests.

### Quick start with uv
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

### Using system Python
```bash
python3 -m pip install -r requirements-dev.txt  # if available, or install pytest, coverage
python3 -m pytest -q
```

### Test files
- tests/test_openai_unit.py — fast unit tests for parsing, error handling, and highlighting
- tests/test_openai_integration.py — real API calls to OpenAI; auto-skipped without OPENAI_API_KEY or if SKIP_INTEGRATION_TESTS=1

### Helpful scripts
- run-tests.sh — convenience wrapper to execute the tests and generate coverage
- test-environment.sh — launches a manual testing zsh session

### Why uv?

- **Speed**: 10-100x faster than pip for dependency resolution and installation
- **Reliability**: Consistent, reproducible environments across machines
- **Modern**: Built with Rust, follows latest Python packaging standards
- **Zero-config**: Works out of the box with minimal setup
- **Compatibility**: Drop-in replacement for pip/venv workflows

## Manual Testing (Fork Enhancement)

This fork includes a comprehensive manual testing environment for validating functionality before deployment.

### Quick Test Setup

1. **Set up your OpenAI API key** (choose one option):
   
   **Option A - Use existing environment variable:**
   ```bash
   # If you already have OPENAI_API_KEY exported in your shell, you're ready to go!
   ```
   
   **Option B - Use .env file:**
   ```bash
   cp .env.example .env
   # Edit .env and set OPENAI_API_KEY=your_actual_api_key
   ```

2. **Install dependencies** (choose your preferred method):

   **🚀 Recommended: Using `uv` (isolated environment):**
   ```bash
   # Install uv if you haven't already: https://docs.astral.sh/uv/
   uv sync --dev  # Installs openai + pygments in isolated .venv
   ```

   **📦 Alternative: Using pip (system-wide):**
   ```bash
   pip3 install openai
   pip3 install pygments  # optional, for syntax highlighting
   ```

3. **Launch test environment:**
   ```bash
   ./test-environment.sh  # Auto-detects uv or falls back to system python
   ```

### What the Test Environment Provides

- **🔒 Isolated zsh session** with all key bindings pre-configured
- **🔑 Environment variable management** via `.env` file (excluded from git)
- **✅ Dependency validation** for Python, openai package, and optional components
- **🎯 Pre-configured key bindings** exactly as documented in the main README
- **🧪 Direct testing aliases** for bypassing zsh integration when debugging
- **🧹 Automatic cleanup** of temporary files when session ends

### Available Test Commands

Once in the test environment, try these key combinations:

| Key Binding | Function | Example |
|-------------|----------|---------|
| `Ctrl + O` | OpenAI command suggestions | Type "list files recursively" then press Ctrl+O |
| `Ctrl + Alt + O` | OpenAI command explanations | Type "find . -name '*.py'" then press Ctrl+Alt+O |
| `Ctrl + P` | GitHub Copilot suggestions | Type "compress all log files" then press Ctrl+P |
| `Ctrl + Alt + P` | GitHub Copilot explanations | Type "tar -czf logs.tar.gz *.log" then press Ctrl+Alt+P |

### Testing Aliases

The test environment includes helpful aliases for debugging:

```bash
# Test OpenAI API directly (bypasses zsh integration)
test-openai-direct

# Test OpenAI explanation directly  
test-openai-explain
```

### Example Test Scenarios

Try these natural language prompts in the test environment:

- **File operations**: "find all python files modified today"
- **System monitoring**: "show memory usage and top processes"  
- **Archive management**: "extract all zip files in current directory"
- **Permission management**: "make all shell scripts executable"
- **Network diagnostics**: "check if port 8080 is open"

### Troubleshooting Test Environment

If you encounter issues:

1. **Missing API key**: The script will create a template `.env` file if none exists
2. **Python dependencies**: The script validates all required packages and provides installation commands
3. **GitHub CLI issues**: GitHub Copilot functionality requires `gh cli` and the copilot extension
4. **Key binding conflicts**: The test environment uses a clean zsh session to avoid conflicts

### Exit Test Environment

- Press `Ctrl + D` or type `exit` to return to your normal shell
- All temporary files are automatically cleaned up on exit

## Security

### Security Status: ⚠️ MEDIUM Risk (Acceptable for Personal/Development Use)

**Last Updated:** October 20, 2025

This project has undergone a comprehensive security audit and remediation. **All identified critical and high-severity vulnerabilities have been resolved.**

### ✅ What's Been Fixed (v0.2.0)

| Vulnerability | Severity | Status |
|--------------|----------|--------|
| Predictable Temporary Files | High (CVSS 7.1) | ✅ **Fixed** - Now uses `mktemp` with automatic cleanup |
| Command Injection via `eval` | Medium (CVSS 5.0) | ✅ **Fixed** - Removed all `eval` usage |
| Missing Input Validation | Medium (CVSS 6.5) | ✅ **Fixed** - Comprehensive validation implemented |
| Network/Subprocess Timeouts | Medium (CVSS 5.0) | ✅ **Fixed** - 30-second timeouts added |
| Unquoted Variables | Low-Medium (CVSS 4.5) | ✅ **Fixed** - All variables properly quoted |

**Test Coverage:** 13/13 unit tests passing including 5 security-specific validation tests

### 🔒 Security Best Practices for Users

1. **Review LLM Suggestions:** Always review generated commands before execution
2. **Protect API Keys:** Use `.env` file with 600 permissions, never commit to version control
3. **Use Trusted Networks:** API communications use HTTPS but ensure network security
4. **Keep Updated:** Apply security updates promptly when released

### 📋 Deployment Recommendations

- ✅ **Personal Use:** Safe for individual developers on personal machines
- ✅ **Development Environments:** Appropriate for development/testing
- ⚠️ **Enterprise/Production:** Additional review recommended (see [SECURITY_AUDIT.md](SECURITY_AUDIT.md))

### 📄 Full Security Details

For complete security audit and remediation details, see [SECURITY_AUDIT.md](SECURITY_AUDIT.md).

**Key Findings:**
- **5 vulnerabilities identified and fixed**
- **Risk reduced from CRITICAL to MEDIUM**
- **All changes tested and validated**
- **Backward compatibility maintained**

### 🐛 Reporting Security Issues

If you discover a security vulnerability, please:
1. **Do not** open a public GitHub issue
2. Email the maintainer directly (see GitHub profile)
3. Include detailed reproduction steps
4. Allow time for remediation before public disclosure

---