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

### OpenAI Backend
- Requires `OPENAI_API_KEY` environment variable
- Requires `pip3 install openai`
- Optional: `pip3 install pygments` for syntax-highlighted explanations

### GitHub Copilot Backend  
- Requires GitHub CLI: `gh` command available
- Requires authentication: `gh auth login --web -h github.com`
- Requires Copilot extension: `gh extension install github/gh-copilot`

## Testing

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
The project also includes demo files in the `demo/` directory that show example interactions. Manual testing is done by using the plugin interactively in a zsh shell.

## Key Implementation Details

- Uses temporary files (`/tmp/zsh-llm-suggestions-result`) to communicate between zsh and Python processes
- Implements custom spinner animation while waiting for LLM responses
- Handles edge cases like empty prompts, missing prerequisites, and API errors
- Supports regenerating suggestions by pressing hotkey again when current buffer matches last result
- Both backends parse and clean LLM responses to extract just the command or explanation text
- OpenAI backend strips markdown code blocks from responses
- GitHub Copilot backend uses complex regex patterns to parse the `gh copilot` CLI output

## File Structure

- `zsh-llm-suggestions.zsh`: Main plugin file to be sourced in `.zshrc`
- `zsh-llm-suggestions-openai.py`: OpenAI backend
- `zsh-llm-suggestions-github-copilot.py`: GitHub Copilot backend  
- `demo/`: Example usage demonstrations
- `README.md`: Installation and usage instructions
- To test the Github workflow files locally, use `act`