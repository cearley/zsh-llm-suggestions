#!/usr/bin/env python3
"""
Unit tests for zsh-llm-suggestions OpenAI backend

These tests don't require API keys and focus on testing the core logic
like markdown parsing, input validation, etc.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock, Mock
from io import StringIO

# Import the new plugin architecture
from zsh_llm_suggestions.base import validate_input, highlight_explanation, MAX_INPUT_LENGTH
from zsh_llm_suggestions.backends.openai import OpenAIBackend


class TestOpenAIMarkdownParsing(unittest.TestCase):
    """Test the markdown parsing logic in OpenAI backend"""

    def setUp(self):
        """Set up test environment"""
        # Mock the OpenAI client
        self.mock_client = MagicMock()
        self.mock_response = MagicMock()
        self.mock_response.choices[0].message.content = "test content"
        self.mock_client.chat.completions.create.return_value = self.mock_response

    @patch('openai.OpenAI')
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    def test_markdown_zsh_block_removal(self, mock_openai_class):
        """Test that ```zsh blocks are properly removed"""
        mock_openai_class.return_value = self.mock_client
        self.mock_response.choices[0].message.content = "```zsh\nls -la\n```"

        backend = OpenAIBackend()
        backend.check_prerequisites()  # Initialize client
        result = backend.generate("list files")

        # Verify the markdown fences were removed
        self.assertEqual(result, "ls -la")

    @patch('openai.OpenAI')
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    def test_markdown_sh_block_removal(self, mock_openai_class):
        """Test that ```sh blocks are properly removed"""
        mock_openai_class.return_value = self.mock_client
        self.mock_response.choices[0].message.content = "```sh\nfind . -name '*.py'\n```"

        backend = OpenAIBackend()
        backend.check_prerequisites()
        result = backend.generate("find python files")

        self.assertEqual(result, "find . -name '*.py'")

    @patch('openai.OpenAI')
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    def test_markdown_generic_block_removal(self, mock_openai_class):
        """Test that generic ``` blocks are properly removed"""
        mock_openai_class.return_value = self.mock_client
        self.mock_response.choices[0].message.content = "```\ngrep -r 'pattern' .\n```"

        backend = OpenAIBackend()
        backend.check_prerequisites()
        result = backend.generate("search for pattern")

        self.assertEqual(result, "grep -r 'pattern' .")

    @patch('openai.OpenAI')
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    def test_mixed_markdown_blocks(self, mock_openai_class):
        """Test handling of mixed text and code blocks"""
        mock_openai_class.return_value = self.mock_client
        self.mock_response.choices[0].message.content = "Here's the command:\n```zsh\ncd /tmp\n```"

        backend = OpenAIBackend()
        backend.check_prerequisites()
        result = backend.generate("navigate to tmp")

        # Should remove markdown and clean up
        self.assertIn("cd /tmp", result)
        self.assertNotIn("```", result)

    def test_missing_api_key(self):
        """Test that missing API key is detected"""
        with patch.dict(os.environ, {}, clear=True):
            backend = OpenAIBackend()
            success, error_msg = backend.check_prerequisites()

            self.assertFalse(success)
            self.assertIn("OPENAI_API_KEY", error_msg)

    @patch('builtins.print')
    @patch('sys.stdin')
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    def test_invalid_mode(self, mock_stdin, mock_print):
        """Test that invalid mode causes an error"""
        mock_stdin.read.return_value = "test input"

        backend = OpenAIBackend()

        # Mock sys.exit to prevent actual exit
        with patch('sys.exit') as mock_exit:
            backend.run('invalid_mode')
            mock_exit.assert_called_with(1)

            # Check that error message was printed
            print_calls = [str(call) for call in mock_print.call_args_list]
            self.assertTrue(any('unknown mode' in str(call) for call in print_calls))


class TestInputValidation(unittest.TestCase):
    """Test the input validation logic"""

    def test_valid_input(self):
        """Test that valid input passes through"""
        result = validate_input("list all files")
        self.assertEqual(result, "list all files")

    def test_input_with_null_bytes(self):
        """Test that input with null bytes is rejected"""
        with self.assertRaises(ValueError) as cm:
            validate_input("test\x00bad")
        self.assertIn("null bytes", str(cm.exception))

    def test_input_too_long(self):
        """Test that overly long input is rejected"""
        long_input = "x" * (MAX_INPUT_LENGTH + 100)
        with self.assertRaises(ValueError) as cm:
            validate_input(long_input)
        self.assertIn("too long", str(cm.exception))

    def test_input_with_control_characters(self):
        """Test that dangerous control characters are stripped"""
        # Test with various control characters
        result = validate_input("test\x01\x02\x03data")
        # Control characters should be stripped, but printable text preserved
        self.assertNotIn("\x01", result)
        self.assertIn("test", result)
        self.assertIn("data", result)

    def test_input_preserves_whitespace(self):
        """Test that newlines, tabs, etc are preserved"""
        input_text = "line1\nline2\ttabbed"
        result = validate_input(input_text)
        self.assertIn("\n", result)
        self.assertIn("\t", result)


class TestHighlightFunction(unittest.TestCase):
    """Test the highlight_explanation function"""

    @patch.dict(os.environ, {}, clear=True)
    def test_highlight_with_pygments(self):
        """Test that explanation gets highlighted when pygments is available"""
        explanation = "# This is a test\nSome code"
        result = highlight_explanation(explanation)
        # Should return string (either highlighted or plain)
        self.assertIsInstance(result, str)

    @patch.dict(os.environ, {'ZSH_LLM_DISABLE_PYGMENTS': '1'})
    def test_highlight_without_pygments(self):
        """Test that highlighting is disabled when env var is set"""
        explanation = "# This is a test"
        result = highlight_explanation(explanation)
        # Should return original text when pygments is disabled
        self.assertEqual(result, explanation)


if __name__ == '__main__':
    unittest.main()
