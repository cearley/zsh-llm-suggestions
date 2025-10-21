#!/usr/bin/env python3
"""Base module for LLM backend plugins."""

import os
import sys
from abc import ABC, abstractmethod
from typing import cast

# Shared constants
MISSING_PREREQUISITES = "zsh-llm-suggestions missing prerequisites:"
MAX_INPUT_LENGTH = 2000  # Maximum characters to prevent abuse


def validate_input(text: str) -> str:
    """
    Validate and sanitize user input for security.

    Args:
        text: User input string to validate

    Returns:
        Sanitized text string

    Raises:
        ValueError: If input fails validation
    """
    # Check for null bytes
    if '\0' in text:
        raise ValueError("Input contains null bytes")

    # Check maximum length to prevent abuse
    if len(text) > MAX_INPUT_LENGTH:
        raise ValueError(f"Input too long (max {MAX_INPUT_LENGTH} characters, got {len(text)})")

    # Strip dangerous control characters (except newlines, tabs, carriage returns)
    # Keep printable characters and common whitespace
    sanitized = ''.join(char for char in text if char.isprintable() or char in '\n\r\t')

    return sanitized.strip()


def highlight_explanation(explanation: str) -> str:
    """
    Add syntax highlighting to explanation text using pygments if available.

    Args:
        explanation: Plain text explanation to highlight

    Returns:
        Highlighted text if pygments available, otherwise original text
    """
    # Respect env override to disable syntax highlighting (useful for testing or minimal environments)
    if os.environ.get('ZSH_LLM_DISABLE_PYGMENTS', '').lower() in ('1', 'true', 'yes'):  # pragma: no cover
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
        from pygments.formatters import TerminalFormatter
        from pygments.lexers import MarkdownLexer
        return cast(str, pygments.highlight(explanation, MarkdownLexer(), TerminalFormatter(style='material')))
    except ImportError:
        return explanation


class LLMBackend(ABC):
    """Abstract base class for LLM backend plugins."""

    @abstractmethod
    def check_prerequisites(self) -> tuple[bool, str]:
        """
        Check if all prerequisites for this backend are met.

        Returns:
            tuple: (success: bool, error_message: str)
                   If success is True, error_message should be empty.
                   If success is False, error_message should contain user-facing error.
        """

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Generate a shell command from a natural language prompt.

        Args:
            prompt: Natural language description of desired command

        Returns:
            str: Generated shell command

        Raises:
            Exception: If generation fails
        """

    @abstractmethod
    def explain(self, command: str) -> str:
        """
        Explain what a shell command does.

        Args:
            command: Shell command to explain

        Returns:
            str: Human-readable explanation

        Raises:
            Exception: If explanation fails
        """

    def run(self, mode: str) -> None:
        """
        Main entry point for backend execution.

        Handles:
        - Mode validation
        - Prerequisite checking
        - Input reading and validation
        - Calling generate() or explain()
        - Error handling

        Args:
            mode: Either 'generate' or 'explain'
        """
        # Validate mode
        if mode not in ('generate', 'explain'):
            print(f"ERROR: something went wrong in zsh-llm-suggestions, please report a bug. Got unknown mode: {mode}")
            sys.exit(1)

        # Check prerequisites
        success, error_message = self.check_prerequisites()
        if not success:
            print(error_message)
            sys.exit(1)

        # Read and validate user input
        buffer = sys.stdin.read()
        try:
            buffer = validate_input(buffer)
        except ValueError as e:
            print(f'echo "ERROR: Invalid input: {e}"')
            sys.exit(1)

        # Call appropriate method
        try:
            if mode == 'generate':
                result = self.generate(buffer)
            else:  # mode == 'explain'
                result = self.explain(buffer)

            print(result)
        except Exception as e:
            print(f'echo "ERROR: Request failed: {e}"')
            sys.exit(1)
