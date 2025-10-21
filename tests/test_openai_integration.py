#!/usr/bin/env python3
"""
Integration tests for zsh-llm-suggestions-openai.py

These tests require a valid OPENAI_API_KEY and make real API calls.
They will be skipped if the API key is not available or if the
SKIP_INTEGRATION_TESTS environment variable is set.
"""

import os
import subprocess
import sys
import time
import unittest

# Add the parent directory to the path to import the script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestOpenAIIntegration(unittest.TestCase):
    """Integration tests that make real API calls"""

    @classmethod
    def setUpClass(cls):
        """Check if integration tests should run"""
        cls.skip_reason = None

        # Skip if explicitly requested
        if os.environ.get("SKIP_INTEGRATION_TESTS", "").lower() in ("1", "true", "yes"):
            cls.skip_reason = "Integration tests disabled by SKIP_INTEGRATION_TESTS"
            return

        # Check for API key in environment
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            # Try loading from .env file
            env_file = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"
            )
            if os.path.exists(env_file):
                with open(env_file) as f:
                    for line in f:
                        if line.startswith("OPENAI_API_KEY="):
                            api_key = line.split("=", 1)[1].strip().strip("\"'")
                            os.environ["OPENAI_API_KEY"] = api_key
                            break

        if not api_key or api_key == "your_openai_api_key_here":
            cls.skip_reason = "No valid OPENAI_API_KEY found"
            return

        # Test if we can import required modules
        try:
            import openai
        except ImportError:
            cls.skip_reason = "OpenAI package not available"
            return

        print(f"\n🔧 Running integration tests with API key: {api_key[:8]}...")

    def setUp(self):
        """Skip tests if setup failed"""
        if self.skip_reason:
            self.skipTest(self.skip_reason)

    def test_generate_simple_command(self):
        """Test generating a simple command via API"""
        # Use uv if available, otherwise python3
        if os.system("command -v uv > /dev/null 2>&1") == 0:
            cmd = ["uv", "run", "python", "-m", "zsh_llm_suggestions.openai_backend", "generate"]
        else:
            cmd = ["python3", "-m", "zsh_llm_suggestions.openai_backend", "generate"]

        process = subprocess.run(
            cmd,
            input="list files in current directory",
            text=True,
            capture_output=True,
            timeout=30,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            env={
                **os.environ,
                "PYTHONPATH": os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"
                ),
            },
        )

        self.assertEqual(process.returncode, 0, f"Script failed: {process.stderr}")

        output = process.stdout.strip()
        self.assertTrue(len(output) > 0, "No output received")

        # Should contain some form of ls command
        self.assertTrue(
            any(cmd in output.lower() for cmd in ["ls", "dir", "find"]),
            f"Output doesn't look like a directory listing command: {output}",
        )

        # Should not contain markdown
        self.assertNotIn("```", output, f"Output contains markdown: {output}")
        self.assertNotIn("zsh", output.lower(), f"Output contains 'zsh' text: {output}")

    def test_explain_command(self):
        """Test explaining a command via API"""
        if os.system("command -v uv > /dev/null 2>&1") == 0:
            cmd = ["uv", "run", "python", "-m", "zsh_llm_suggestions.openai_backend", "explain"]
        else:
            cmd = ["python3", "-m", "zsh_llm_suggestions.openai_backend", "explain"]

        process = subprocess.run(
            cmd,
            input="ls -la",
            text=True,
            capture_output=True,
            timeout=30,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            env={
                **os.environ,
                "PYTHONPATH": os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"
                ),
            },
        )

        self.assertEqual(process.returncode, 0, f"Script failed: {process.stderr}")

        output = process.stdout.strip()
        self.assertTrue(len(output) > 0, "No explanation received")

        # Should contain explanation keywords
        self.assertTrue(
            any(
                word in output.lower() for word in ["list", "files", "directory", "long", "format"]
            ),
            f"Output doesn't look like an ls explanation: {output}",
        )

    def test_command_with_markdown_response(self):
        """Test that markdown responses are properly cleaned"""
        if os.system("command -v uv > /dev/null 2>&1") == 0:
            cmd = ["uv", "run", "python", "-m", "zsh_llm_suggestions.openai_backend", "generate"]
        else:
            cmd = ["python3", "-m", "zsh_llm_suggestions.openai_backend", "generate"]

        # Use a query that's likely to generate markdown
        process = subprocess.run(
            cmd,
            input="write a bash command to find all python files modified in the last 7 days",
            text=True,
            capture_output=True,
            timeout=30,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            env={
                **os.environ,
                "PYTHONPATH": os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"
                ),
            },
        )

        self.assertEqual(process.returncode, 0, f"Script failed: {process.stderr}")

        output = process.stdout.strip()
        self.assertTrue(len(output) > 0, "No output received")

        # Should not contain any markdown artifacts
        self.assertNotIn("```zsh", output, f"Output contains ```zsh: {output}")
        self.assertNotIn("```sh", output, f"Output contains ```sh: {output}")
        self.assertNotIn("```", output, f"Output contains ```: {output}")

        # Should contain a command that makes sense
        self.assertTrue(
            any(cmd in output.lower() for cmd in ["find", "locate", "ls"]),
            f"Output doesn't look like a file search command: {output}",
        )

    def test_rate_limiting_handling(self):
        """Test that the script handles rate limiting gracefully"""
        script_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "src",
            "zsh_llm_suggestions",
            "openai_backend.py",
        )

        if os.system("command -v uv > /dev/null 2>&1") == 0:
            cmd = ["uv", "run", "python", script_path, "generate"]
        else:
            cmd = ["python3", script_path, "generate"]

        # Make multiple rapid requests to potentially trigger rate limiting
        for i in range(3):
            process = subprocess.run(
                cmd,
                input=f"list files in directory number {i}",
                text=True,
                capture_output=True,
                timeout=30,
            )

            # Should either succeed or fail gracefully (not crash)
            self.assertIn(
                process.returncode,
                [0, 1],
                f"Script crashed with code {process.returncode}: {process.stderr}",
            )

            if process.returncode != 0:
                # If it fails, should have some error output
                self.assertTrue(
                    len(process.stdout) > 0 or len(process.stderr) > 0, "Script failed silently"
                )

            # Small delay between requests
            time.sleep(1)


class TestEnvironmentDetection(unittest.TestCase):
    """Test that the script works in different environments"""

    def test_uv_environment_detection(self):
        """Test that script works when run with uv"""
        if os.system("command -v uv > /dev/null 2>&1") != 0:
            self.skipTest("uv not available")

        # Test without API key (should fail gracefully)
        env = os.environ.copy()
        env.pop("OPENAI_API_KEY", None)

        process = subprocess.run(
            ["uv", "run", "python", "-m", "zsh_llm_suggestions.openai_backend", "generate"],
            input="test command",
            text=True,
            capture_output=True,
            env=env,
            timeout=10,
        )

        # Should fail gracefully with helpful message
        self.assertNotEqual(process.returncode, 0)
        self.assertIn("OPENAI_API_KEY", process.stdout)

    def test_system_python_environment(self):
        """Test that script works with system python"""
        # Test without API key (should fail gracefully)
        env = os.environ.copy()
        env.pop("OPENAI_API_KEY", None)
        # Add current directory to PYTHONPATH so module can be imported
        env["PYTHONPATH"] = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"
        )

        process = subprocess.run(
            ["python3", "-m", "zsh_llm_suggestions.openai_backend", "generate"],
            input="test command",
            text=True,
            capture_output=True,
            env=env,
            timeout=10,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        )

        # Should either work or fail gracefully
        if process.returncode != 0:
            self.assertIn("OPENAI_API_KEY", process.stdout)


if __name__ == "__main__":
    # Add some helpful output for manual testing
    print("🧪 OpenAI Integration Tests")
    print("=" * 50)

    if os.environ.get("SKIP_INTEGRATION_TESTS"):
        print("⏭️  Integration tests disabled by SKIP_INTEGRATION_TESTS")
    elif not os.environ.get("OPENAI_API_KEY"):
        print("⚠️  No OPENAI_API_KEY found - integration tests will be skipped")
        print("   Set your API key or create a .env file to run integration tests")
    else:
        print("🚀 Running integration tests (this may take a moment)...")

    print()
    unittest.main(verbosity=2)
