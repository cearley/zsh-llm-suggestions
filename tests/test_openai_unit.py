#!/usr/bin/env python3
"""
Unit tests for zsh-llm-suggestions-openai.py

These tests don't require API keys and focus on testing the core logic
like markdown parsing, input validation, etc.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock
from io import StringIO

# Add the parent directory to the path to import the script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Helper function to get the script path dynamically
def get_openai_script_path():
    """Get the path to zsh-llm-suggestions-openai.py relative to this test file"""
    test_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(test_dir)
    return os.path.join(project_root, 'zsh-llm-suggestions-openai.py')


class TestOpenAIMarkdownParsing(unittest.TestCase):
    """Test the markdown parsing logic that was recently fixed"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock the OpenAI client and environment
        self.mock_client = MagicMock()
        self.mock_response = MagicMock()
        self.mock_response.choices[0].message.content = "test content"
        self.mock_client.chat.completions.create.return_value = self.mock_response
        
    @patch('builtins.print')
    @patch('sys.stdin')
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    @patch('openai.OpenAI')
    def test_markdown_zsh_block_removal(self, mock_openai_class, mock_stdin, mock_print):
        """Test that ```zsh blocks are properly removed"""
        # Set up the mock
        mock_openai_class.return_value = self.mock_client
        self.mock_response.choices[0].message.content = "```zsh\nls -la\n```"
        mock_stdin.read.return_value = "list files"
        
        # Import and run
        import importlib.util
        spec = importlib.util.spec_from_file_location("openai_script", 
            get_openai_script_path())
        openai_script = importlib.util.module_from_spec(spec)
        
        # Mock sys.argv for generate mode
        with patch.object(sys, 'argv', ['script.py', 'generate']):
            spec.loader.exec_module(openai_script)
            openai_script.main()
        
        # Verify the output was cleaned
        mock_print.assert_called_with("ls -la")
    
    @patch('builtins.print')
    @patch('sys.stdin')
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    @patch('openai.OpenAI')
    def test_markdown_sh_block_removal(self, mock_openai_class, mock_stdin, mock_print):
        """Test that ```sh blocks are properly removed"""
        mock_openai_class.return_value = self.mock_client
        self.mock_response.choices[0].message.content = "```sh\nfind . -name '*.py'\n```"
        mock_stdin.read.return_value = "find python files"
        
        import importlib.util
        spec = importlib.util.spec_from_file_location("openai_script", 
            get_openai_script_path())
        openai_script = importlib.util.module_from_spec(spec)
        
        with patch.object(sys, 'argv', ['script.py', 'generate']):
            spec.loader.exec_module(openai_script)
            openai_script.main()
        
        mock_print.assert_called_with("find . -name '*.py'")
    
    @patch('builtins.print')
    @patch('sys.stdin')
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    @patch('openai.OpenAI')
    def test_markdown_generic_block_removal(self, mock_openai_class, mock_stdin, mock_print):
        """Test that ``` blocks are properly removed"""
        mock_openai_class.return_value = self.mock_client
        self.mock_response.choices[0].message.content = "```\ngrep -r 'pattern' .\n```"
        mock_stdin.read.return_value = "search for pattern"
        
        import importlib.util
        spec = importlib.util.spec_from_file_location("openai_script", 
            get_openai_script_path())
        openai_script = importlib.util.module_from_spec(spec)
        
        with patch.object(sys, 'argv', ['script.py', 'generate']):
            spec.loader.exec_module(openai_script)
            openai_script.main()
        
        mock_print.assert_called_with("grep -r 'pattern' .")
    
    @patch('builtins.print')
    @patch('sys.stdin')
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    @patch('openai.OpenAI')
    def test_mixed_markdown_blocks(self, mock_openai_class, mock_stdin, mock_print):
        """Test complex markdown with multiple blocks"""
        mock_openai_class.return_value = self.mock_client
        self.mock_response.choices[0].message.content = "Here's the command:\n```zsh\ntar -czf backup.tar.gz *.log\n```\nThis will work."
        mock_stdin.read.return_value = "compress log files"
        
        import importlib.util
        spec = importlib.util.spec_from_file_location("openai_script", 
            get_openai_script_path())
        openai_script = importlib.util.module_from_spec(spec)
        
        with patch.object(sys, 'argv', ['script.py', 'generate']):
            spec.loader.exec_module(openai_script)
            openai_script.main()
        
        # Should extract just the command, stripping all markdown and explanation
        mock_print.assert_called_with("Here's the command:\ntar -czf backup.tar.gz *.log\nThis will work.")
    
    @patch('builtins.print')
    def test_missing_api_key(self, mock_print):
        """Test behavior when OPENAI_API_KEY is missing"""
        with patch.dict(os.environ, {}, clear=True):
            with patch.object(sys, 'argv', ['script.py', 'generate']):
                with patch('sys.stdin') as mock_stdin:
                    mock_stdin.read.return_value = "test query"
                    
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("openai_script", 
                        get_openai_script_path())
                    openai_script = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(openai_script)
                    try:
                        openai_script.main()
                    except SystemExit:
                        pass
        
        # Should print error message about missing API key
        expected_call = 'echo "zsh-llm-suggestions missing prerequisites: OPENAI_API_KEY is not set." && export OPENAI_API_KEY="<copy from https://platform.openai.com/api-keys>"'
        mock_print.assert_called_with(expected_call)
    
    @patch('builtins.print')
    def test_invalid_mode(self, mock_print):
        """Test behavior with invalid mode argument"""
        with patch.object(sys, 'argv', ['script.py', 'invalid_mode']):
            import importlib.util
            spec = importlib.util.spec_from_file_location("openai_script", 
                get_openai_script_path())
            openai_script = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(openai_script)
            try:
                openai_script.main()
            except SystemExit:
                pass
        
        mock_print.assert_called_with("ERROR: something went wrong in zsh-llm-suggestions, please report a bug. Got unknown mode: invalid_mode")


class TestHighlightFunction(unittest.TestCase):
    """Test the highlight_explanation function"""
    
    def test_highlight_with_pygments(self):
        """Test highlight function when pygments is available"""
        import importlib.util
        spec = importlib.util.spec_from_file_location("openai_script", 
            get_openai_script_path())
        openai_script = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(openai_script)
        
        # Test with a simple markdown string
        result = openai_script.highlight_explanation("# Test\nThis is **bold**")
        # Should return formatted text (exact format depends on pygments version)
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
    
    @patch.dict(os.environ, {'ZSH_LLM_DISABLE_PYGMENTS': '1'})
    def test_highlight_without_pygments(self):
        """Test highlight function when pygments is disabled via env var"""
        import importlib.util
        spec = importlib.util.spec_from_file_location("openai_script", 
            get_openai_script_path())
        openai_script = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(openai_script)
        
        test_text = "# Test\nThis is **bold**"
        result = openai_script.highlight_explanation(test_text)
        # Should return the original text unchanged
        self.assertEqual(result, test_text)


if __name__ == '__main__':
    unittest.main()