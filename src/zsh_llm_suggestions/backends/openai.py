#!/usr/bin/env python3
"""OpenAI backend for zsh-llm-suggestions."""

import os
import re
from typing import TYPE_CHECKING, Optional

from ..base import MISSING_PREREQUISITES, LLMBackend, highlight_explanation

if TYPE_CHECKING:
    from openai import OpenAI


class OpenAIBackend(LLMBackend):
    """OpenAI GPT-4 backend implementation."""

    def __init__(self) -> None:
        """Initialize OpenAI backend."""
        self.client: Optional[OpenAI] = None

    def check_prerequisites(self) -> tuple[bool, str]:
        """Check if OpenAI prerequisites are met."""
        # Check if openai package is installed
        try:
            import openai
        except ImportError:
            return (False, f'echo "{MISSING_PREREQUISITES} Install OpenAI Python API." && pip3 install openai')

        # Check if API key is set
        api_key = os.environ.get('OPENAI_API_KEY')
        if api_key is None:
            return (False,
                    f'echo "{MISSING_PREREQUISITES} OPENAI_API_KEY is not set." && '
                    f'export OPENAI_API_KEY="<copy from https://platform.openai.com/api-keys>"')

        # Initialize client
        import openai
        self.client = openai.OpenAI(api_key=api_key)

        return (True, "")

    def generate(self, prompt: str) -> str:
        """Generate a shell command from a prompt."""
        assert self.client is not None, "OpenAI client not initialized"

        system_message = """You are a zsh shell expert, please write a ZSH command that solves my problem.
You should only output the completed command, no need to include any other explanation."""

        messages = [
            {"role": 'system', "content": system_message},
            {"role": "user", "content": prompt}
        ]

        # Security: Add timeout to prevent indefinite hangs
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=messages,  # type: ignore[arg-type]
                temperature=0.2,
                max_tokens=1000,
                frequency_penalty=0.0,
                timeout=30.0  # 30 second timeout
            )
        except Exception as e:
            raise Exception(f"API request failed: {e}") from e

        content = response.choices[0].message.content
        if content is None:
            raise Exception("API returned empty response")
        result = content.strip()

        # Strip Markdown code fences cleanly (including the newline that follows/precedes)
        # Remove opening fences like ```zsh or ```sh
        result = re.sub(r'(?m)^```(?:zsh|sh)?\s*\n?', '', result)
        # Remove closing fences ``` (and an optional preceding newline)
        result = re.sub(r'(?m)\n?^```\s*$', '', result)
        # Collapse multiple blank lines resulting from fence removal
        result = re.sub(r'\n{3,}', '\n\n', result).strip()

        return result

    def explain(self, command: str) -> str:
        """Explain what a shell command does."""
        assert self.client is not None, "OpenAI client not initialized"

        system_message = """You are a zsh shell expert, please briefly explain how the given command works. Be as concise as possible. Use Markdown syntax for formatting."""

        messages = [
            {"role": 'system', "content": system_message},
            {"role": "user", "content": command}
        ]

        # Security: Add timeout to prevent indefinite hangs
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=messages,  # type: ignore[arg-type]
                temperature=0.2,
                max_tokens=1000,
                frequency_penalty=0.0,
                timeout=30.0  # 30 second timeout
            )
        except Exception as e:
            raise Exception(f"API request failed: {e}") from e

        content = response.choices[0].message.content
        if content is None:
            raise Exception("API returned empty response")
        result = content.strip()

        # Apply syntax highlighting if available
        return highlight_explanation(result)
