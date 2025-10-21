# zsh-llm-suggestions

LLM-powered command suggestions and explanations for zsh. Type what you want to do in natural language, press a hotkey, and get the shell command you need.

[![CI](https://github.com/cearley/zsh-llm-suggestions/actions/workflows/ci.yml/badge.svg)](https://github.com/cearley/zsh-llm-suggestions/actions)
[![Security](https://img.shields.io/badge/security-major%20vulnerabilities%20resolved-yellow.svg)](SECURITY_AUDIT.md)
[![License](https://img.shields.io/github/license/cearley/zsh-llm-suggestions)](LICENSE)

## Demo

![Demo of zsh-llm-suggestions](https://github.com/stefanheule/zsh-llm-suggestions/blob/master/zsh-llm-suggestions.gif?raw=true)

## Project Status

This project was originally forked from [zsh-llm-suggestions](https://github.com/stefanheule/zsh-llm-suggestions) by Stefan Heule. Since the fork, the codebase has undergone substantial modernization and restructuring, including:

- Refactoring for modern Python (type hints, pathlib, exception handling)
- Enhanced code quality tooling (Ruff, mypy, pytest-randomly, pre-commit)
- Improved logging, error handling, and documentation standards
- Modular architecture and expanded developer workflows

As a result, the majority of the code, features, and design now reflect original work beyond the initial fork.

**Attribution:**  
This project retains the original license and credits the upstream author. See `LICENSE` for details.

**Status:** Acceptable for personal and development use (see [Security](#security) section)

**Key Improvements:**
- **Security hardened** - All 5 critical/high vulnerabilities resolved (v0.2.0)
- **Easy installation** - One-command setup with `uv tool install` (v0.1.0)
- **Active maintenance** - Regular updates and improvements
- **Well-tested** - 13 unit tests with 62% coverage

**Recent Changes:**
- v0.2.0 (October 2025): Security hardening release
  - Secure temporary file handling with automatic cleanup
  - Comprehensive input validation (length limits, null byte detection, sanitization)
  - 30-second timeouts on all network operations
  - Removed unsafe `eval` usage
  - All variables properly quoted
- v0.1.0 (October 2025): `uv tool install` support with interactive installer

[Full release notes](https://github.com/cearley/zsh-llm-suggestions/releases)

## Quick Start

### Option 1: Install via uv (Recommended)

```bash
# Install globally
uv tool install git+https://github.com/cearley/zsh-llm-suggestions

# Run the interactive installer (automatically configures source line and key bindings)
zsh-llm-install

# Restart your shell
source ~/.zshrc
```

### Option 2: Git Clone

```bash
# Clone the repository
git clone https://github.com/cearley/zsh-llm-suggestions.git ~/.local/share/zsh-llm-suggestions
cd ~/.local/share/zsh-llm-suggestions

# Option A: Use the interactive installer (requires uv)
uv sync --dev  # Set up dependencies
uv run zsh-llm-install  # Automatically configures source line and key bindings

# Option B: Manual configuration
# Add to ~/.zshrc
echo 'source ~/.local/share/zsh-llm-suggestions/zsh-llm-suggestions.zsh' >> ~/.zshrc

# Configure key bindings in ~/.zshrc
bindkey '^o' zsh_llm_suggestions_openai
bindkey '^xo' zsh_llm_suggestions_openai_explain       # Ctrl+X then O
bindkey '^p' zsh_llm_suggestions_github_copilot
bindkey '^xp' zsh_llm_suggestions_github_copilot_explain  # Ctrl+X then P

# Restart your shell
source ~/.zshrc
```

## Configuration

### OpenAI Backend

1. Get an API key from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Set the environment variable:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

**Dependencies:** Python packages are automatically installed:
- **uv tool install**: All dependencies included automatically
- **git clone with uv**: Run `uv sync --dev` to install dependencies
- **git clone without uv** (legacy): Manually install with `pip3 install openai pygments`

### GitHub Copilot Backend

1. Install GitHub CLI: [github.com/cli/cli#installation](https://github.com/cli/cli#installation)
2. Authenticate:
   ```bash
   gh auth login --web -h github.com
   ```
3. Install the Copilot extension:
   ```bash
   gh extension install github/gh-copilot
   ```

## Usage

### Generate Commands

Type what you want to do in natural language, then press your configured hotkey:

**Examples:**
```bash
list files recursively                    # Press Ctrl+O → suggests: find . -type f
show memory usage and top processes       # Press Ctrl+O → suggests: ps aux --sort=-%mem | head
compress all log files                    # Press Ctrl+P → suggests: tar -czf logs.tar.gz *.log
```

**Key bindings:**
- `Ctrl+O` - Get command suggestion from OpenAI
- `Ctrl+P` - Get command suggestion from GitHub Copilot
- Press the same key again if you want a different suggestion

If you don't like the suggestion, press the hotkey again to get a new one.

### Explain Commands

Type or paste a command you don't understand, then press the explain hotkey:

**Examples:**
```bash
find . -name '*.py' -exec grep -l 'TODO' {} \;    # Press Ctrl+X then O → explains the command
tar -czf backup.tar.gz --exclude='*.log' ./data   # Press Ctrl+X then P → explains the command
```

**Key bindings:**
- `Ctrl+X` then `O` - Explain command using OpenAI
- `Ctrl+X` then `P` - Explain command using GitHub Copilot

**Note:** These keybindings work universally across all terminals, including IDE terminals (PyCharm, VS Code, etc.).

## Commands

### When installed via `uv tool install`

These commands are available directly:

```bash
zsh-llm-openai      # OpenAI backend (called by Ctrl+O)
zsh-llm-copilot     # GitHub Copilot backend (called by Ctrl+P)
zsh-llm-install     # Interactive setup wizard
zsh-llm-uninstall   # Remove zsh integration
zsh-llm-status      # Check installation status and version
```

### When installed via git clone

Use `uv run` to access the same commands:

```bash
cd ~/.local/share/zsh-llm-suggestions

uv run zsh-llm-install    # Interactive setup wizard
uv run zsh-llm-uninstall  # Remove zsh integration
uv run zsh-llm-status     # Check installation status and version

# Backend commands (automatically used by key bindings)
uv run zsh-llm-openai     # OpenAI backend
uv run zsh-llm-copilot    # GitHub Copilot backend
```

## Updating

**uv installation:**
```bash
uv tool upgrade zsh-llm-suggestions
```

**Git clone installation:**
```bash
cd ~/.local/share/zsh-llm-suggestions
git pull origin master
source ~/.zshrc
```

## Uninstalling

**uv installation:**
```bash
zsh-llm-uninstall    # Remove zsh integration
uv tool uninstall zsh-llm-suggestions  # Remove the tool
```

**Git clone installation:**
```bash
cd ~/.local/share/zsh-llm-suggestions

# Option A: Use the uninstaller (requires uv)
uv run zsh-llm-uninstall  # Automatically removes source line and key bindings

# Option B: Manual removal
# Remove the source line from ~/.zshrc
# Remove key binding lines from ~/.zshrc
rm -rf ~/.local/share/zsh-llm-suggestions
```

## Security

### Status: MEDIUM Risk (Acceptable for Personal/Development Use)

This project has undergone a comprehensive security audit. All 5 critical and high-severity vulnerabilities identified in the audit have been resolved in v0.2.0.

**Fixed vulnerabilities:**
- Predictable temporary files (High severity)
- Command injection via eval (Medium severity)
- Missing input validation (Medium severity)
- Network/subprocess timeouts (Medium severity)
- Unquoted variables (Low-Medium severity)

**Best practices:**
- Always review LLM-generated commands before execution
- Protect your API keys (use `.env` file with 600 permissions, never commit to version control)
- Use trusted networks
- Keep the tool updated

**Full details:** See [SECURITY_AUDIT.md](SECURITY_AUDIT.md) for the complete security audit and remediation details.

**Report security issues:** Do not open public GitHub issues. Email the maintainer directly (see GitHub profile).

## Warning

**Costs:** Both OpenAI and GitHub Copilot are paid services. You are responsible for any charges incurred.

**Review commands:** LLMs can suggest incorrect or dangerous commands. Always review suggestions before executing them.

## Documentation

- [CONTRIBUTING.md](CONTRIBUTING.md) - Development setup, testing, and contribution guidelines
- [RELEASING.md](RELEASING.md) - Release process for maintainers
- [SECURITY_AUDIT.md](SECURITY_AUDIT.md) - Comprehensive security audit and remediation details
- [CLAUDE.md](CLAUDE.md) - AI-assisted development guidelines

## License

[MIT License](LICENSE)

## Credits

Original project by [Stefan Heule](https://github.com/stefanheule/zsh-llm-suggestions)

This fork maintained by [Craig Earley](https://github.com/cearley)
