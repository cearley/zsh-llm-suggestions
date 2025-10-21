#!/usr/bin/env python3
"""GitHub Copilot backend entry point for zsh-llm-suggestions."""

import sys

from .backends.copilot import CopilotBackend


def main() -> None:
    """Main entry point for Copilot backend."""
    if len(sys.argv) < 2:
        print("ERROR: Mode argument required (generate or explain)")
        sys.exit(1)

    mode = sys.argv[1]
    backend = CopilotBackend()
    backend.run(mode)


if __name__ == "__main__":
    main()
