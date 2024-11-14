import sys
sys.path.append('../src')

import unittest
from unittest.mock import patch, MagicMock
import os
from llm_interface import gpt_query, metric_prompts


class TestLLMInterface(unittest.TestCase):

    @patch('os.getenv')
    def test_abs_llm_model_path(self, mock_getenv):
        # Mock the environment variable
        mock_getenv.return_value = '/mock/path/to/model'

        # Check the absolute model path
        abs_model_path = os.path.join(os.path.dirname(__file__), os.getenv('LLM_MODEL_PATH'))
        self.assertEqual(abs_model_path, '/mock/path/to/model')

    @patch('gpt4all.GPT4All')
    @patch('llm_interface.os.getenv')
    def test_llm_model_loading(self, mock_getenv, mock_GPT4All):
        # Mock the environment variable
        mock_getenv.return_value = '/mock/path/to/model'
        
        # Mock the GPT4All model instance
        mock_llm = MagicMock()
        mock_GPT4All.return_value = mock_llm

        # Ensure that GPT4All is instantiated with the correct path
        llm = mock_GPT4All('/mock/path/to/model', device="cpu", verbose=False, allow_download=False)
        mock_GPT4All.assert_called_once_with('/mock/path/to/model', device="cpu", verbose=False, allow_download=False)

if __name__ == '__main__':
    unittest.main()
