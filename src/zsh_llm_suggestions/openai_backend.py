#!/usr/bin/env python3
"""OpenAI backend entry point for zsh-llm-suggestions."""

import sys

from .backends.openai import OpenAIBackend


def main():
    """Main entry point for OpenAI backend."""
    if len(sys.argv) < 2:
        print("ERROR: Mode argument required (generate or explain)")
        sys.exit(1)

    mode = sys.argv[1]
    backend = OpenAIBackend()
    backend.run(mode)


if __name__ == '__main__':
    main()
