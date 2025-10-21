"""LLM backend plugins for zsh-llm-suggestions."""

from .copilot import CopilotBackend
from .openai import OpenAIBackend

__all__ = ["OpenAIBackend", "CopilotBackend"]
