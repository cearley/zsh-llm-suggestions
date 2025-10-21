#!/usr/bin/env python3
"""GitHub Copilot backend for zsh-llm-suggestions."""

import logging
import os
import re
import subprocess

from ..base import MISSING_PREREQUISITES, LLMBackend

logger = logging.getLogger(__name__)


class CopilotBackend(LLMBackend):
    """GitHub Copilot backend implementation."""

    def check_prerequisites(self) -> tuple[bool, str]:
        """Check if GitHub Copilot prerequisites are met."""
        # Check if gh CLI is installed
        logger.debug("Checking for GitHub CLI (gh)")
        try:
            subprocess.run(
                ["gh", "version"],
                text=True,
                stderr=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                check=True,
            )
            logger.info("GitHub Copilot backend prerequisites satisfied")
        except (FileNotFoundError, subprocess.CalledProcessError):
            logger.error("GitHub CLI (gh) not found or not working")
            return (
                False,
                f'echo "{MISSING_PREREQUISITES} Install GitHub CLI first by following '
                f'https://github.com/cli/cli#installation"',
            )

        return (True, "")

    def generate(self, prompt: str) -> str:
        """Generate a shell command from a prompt."""
        logger.debug(f"Sending generate request to GitHub Copilot (prompt length: {len(prompt)})")
        command = ["gh", "copilot", "suggest", "-t", "shell", prompt]
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Security: Add timeout to prevent indefinite hangs
        try:
            output, error = process.communicate(timeout=30.0)  # 30 second timeout
            logger.debug("GitHub Copilot request completed")
        except subprocess.TimeoutExpired:
            logger.error("GitHub Copilot request timed out after 30 seconds")
            process.kill()
            process.communicate()  # Clean up
            raise Exception("Request timed out after 30 seconds") from None

        # Check for authentication errors
        if "Error: No valid OAuth token detected" in error:
            logger.error("GitHub Copilot authentication failed: No valid OAuth token")
            raise Exception(
                f"{MISSING_PREREQUISITES} Authenticate with github first: gh auth login --web -h github.com"
            )

        # Check for missing copilot extension
        if 'unknown command "copilot" for "gh"' in error:
            logger.error("GitHub Copilot extension not found")
            if (
                "You are not logged into any GitHub hosts"
                in subprocess.run(
                    ["gh", "auth", "status"],
                    text=True,
                    stderr=subprocess.PIPE,
                    stdout=subprocess.DEVNULL,
                ).stderr
            ):
                logger.error("Not authenticated with GitHub")
                raise Exception(
                    f"{MISSING_PREREQUISITES} Authenticate with github first: gh auth login --web -h github.com"
                )
            raise Exception(
                f"{MISSING_PREREQUISITES} Install github copilot extension first: gh extension install github/gh-copilot"
            )

        # Check for no suggestion
        if "Suggestion not readily available. Please revise for better results." in output:
            logger.warning("GitHub Copilot returned no suggestion")
            return "No answer from GitHub CoPilot."

        # Strip unnecessary output
        needle = "# Suggestion:"
        idx = output.find(needle)
        if idx != -1:
            output = output[idx + len(needle) :]
        idx = output.find("\x0a\x0a\x1b\x37\x1b\x5b\x3f")
        if idx != -1:
            output = output[:idx]

        output = output.strip()

        # Something went wrong
        if output == "" and error != "":
            raise Exception(error)

        return output

    def explain(self, command: str) -> str:
        """Explain what a shell command does."""
        logger.debug(f"Sending explain request to GitHub Copilot (command length: {len(command)})")
        env = os.environ.copy()
        env["CLICOLOR_FORCE"] = "1"

        cmd = ["gh", "copilot", "explain", command]
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )

        # Security: Add timeout to prevent indefinite hangs
        try:
            output, error = process.communicate(timeout=30.0)  # 30 second timeout
            logger.debug("GitHub Copilot request completed")
        except subprocess.TimeoutExpired:
            logger.error("GitHub Copilot request timed out after 30 seconds")
            process.kill()
            process.communicate()  # Clean up
            raise Exception("Request timed out after 30 seconds") from None

        # Check for authentication errors
        if "Error: No valid OAuth token detected" in error:
            logger.error("GitHub Copilot authentication failed: No valid OAuth token")
            raise Exception(
                f"{MISSING_PREREQUISITES} Authenticate with github first: gh auth login --web -h github.com"
            )

        # Check for missing copilot extension
        if 'unknown command "copilot" for "gh"' in error:
            logger.error("GitHub Copilot extension not found")
            if (
                "You are not logged into any GitHub hosts"
                in subprocess.run(
                    ["gh", "auth", "status"],
                    text=True,
                    stderr=subprocess.PIPE,
                    stdout=subprocess.DEVNULL,
                ).stderr
            ):
                logger.error("Not authenticated with GitHub")
                raise Exception(
                    f"{MISSING_PREREQUISITES} Authenticate with github first: gh auth login --web -h github.com"
                )
            raise Exception(
                f"{MISSING_PREREQUISITES} Install github copilot extension first: gh extension install github/gh-copilot"
            )

        # Check for no explanation
        if "Suggestion not readily available. Please revise for better results." in output:
            logger.warning("GitHub Copilot returned no explanation")
            return "No answer from GitHub CoPilot."

        # Strip unnecessary output
        needle = "\x45\x78\x70\x6c\x61\x6e\x61\x74\x69\x6f\x6e\x1b\x5b\x30\x6d\x1b\x5b\x31\x6d\x3a"
        idx = output.find(needle)
        if idx != -1:
            output = output[idx + len(needle) :]
        output = re.sub(r"^\x1b\x5b\x30\x6d( +\n)*", "\x1b\x5b\x30\x6d", output)

        output = output.strip()

        # Something went wrong
        if output == "" and error != "":
            raise Exception(error)

        return output
