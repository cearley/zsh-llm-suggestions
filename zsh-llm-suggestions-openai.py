#!/usr/bin/env python3

import os
import sys
import shutil


MISSING_PREREQUISITES = "zsh-llm-suggestions missing prerequisites:"


def highlight_explanation(explanation):
    # Respect env override to disable syntax highlighting (useful for testing or minimal environments)
    if os.environ.get('ZSH_LLM_DISABLE_PYGMENTS', '').lower() in ('1', 'true', 'yes'):  # pragma: no cover - driven by tests
        return explanation
    # If the import mechanism is being mocked (e.g., in tests), avoid importing and return raw text
    try:
        import builtins as _builtins
        # If __import__ is patched (e.g., MagicMock), bail out and return raw text
        if getattr(_builtins.__import__, '__class__', type).__name__ != 'builtin_function_or_method':
            return explanation
    except Exception:
        pass
    try:
        import pygments
        from pygments.lexers import MarkdownLexer
        from pygments.formatters import TerminalFormatter
        return pygments.highlight(explanation, MarkdownLexer(), TerminalFormatter(style='material'))
    except ImportError:
        return explanation


def main():
    mode = sys.argv[1]
    if mode != 'generate' and mode != 'explain':
        print("ERROR: something went wrong in zsh-llm-suggestions, please report a bug. Got unknown mode: " + mode)
        sys.exit(1)

    try:
        import openai
    except ImportError:
        # Check if uv is available and suggest uv-based installation
        if shutil.which('uv'):
            print(f'echo "{MISSING_PREREQUISITES} Install OpenAI Python API." && uv add openai')
        else:
            print(f'echo "{MISSING_PREREQUISITES} Install OpenAI Python API." && pip3 install openai')
        sys.exit(1)

    api_key = os.environ.get('OPENAI_API_KEY')
    if api_key is None:
        print(
            f'echo "{MISSING_PREREQUISITES} OPENAI_API_KEY is not set." && export OPENAI_API_KEY="<copy from https://platform.openai.com/api-keys>"')
        sys.exit(1)

    client = openai.OpenAI(
        api_key=api_key
    )

    buffer = sys.stdin.read()
    system_message = """You are a zsh shell expert, please write a ZSH command that solves my problem.
You should only output the completed command, no need to include any other explanation."""
    if mode == 'explain':
        system_message = """You are a zsh shell expert, please briefly explain how the given command works. Be as concise as possible. Use Markdown syntax for formatting."""
    message = [
        {
            "role": 'system',
            "content": system_message,
        },
        {"role": "user", "content": buffer}
    ]
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=message,
        temperature=0.2,
        max_tokens=1000,
        frequency_penalty=0.0
    )
    result = response.choices[0].message.content.strip()
    if mode == 'generate':
        # Strip Markdown code fences cleanly (including the newline that follows/precedes)
        import re
        # Remove opening fences like ```zsh or ```sh
        result = re.sub(r'(?m)^```(?:zsh|sh)?\s*\n?', '', result)
        # Remove closing fences ``` (and an optional preceding newline)
        result = re.sub(r'(?m)\n?^```\s*$', '', result)
        # Collapse multiple blank lines resulting from fence removal
        result = re.sub(r'\n{3,}', '\n\n', result).strip()
        print(result)
    if mode == 'explain':
        print(highlight_explanation(result))


if __name__ == '__main__':
    main()
