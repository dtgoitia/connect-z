import sys
import unittest
from unittest.mock import call, patch

import connectz


EXISTING_FILE = 'good_file'
NON_EXISTING_FILE = 'non_existing_file'


class ConnectzTest(unittest.TestCase):

    @patch.object(sys, 'argv', ['connectz.py'])
    @patch('connectz.log')
    def test_no_input_files_provided(self, mocked_log):
        connectz.main()
        expected_log_calls = (call('Provide one input file'),)
        mocked_log.assert_has_calls(expected_log_calls)

    @patch.object(sys, 'argv', ['connectz.py', EXISTING_FILE, EXISTING_FILE, NON_EXISTING_FILE])
    @patch('connectz.log')
    def test_many_input_files_provided(self, mocked_log):
        connectz.main()
        expected_log_calls = (call('Provide one input file'),)
        mocked_log.assert_has_calls(expected_log_calls)

    @patch.object(sys, 'argv', ['connectz.py', 'illegal_row'])
    @patch('connectz.log')
    def test_illegal_row(self, mocked_log):
        connectz.main()
        expected_log_calls = (call('5'),)
        mocked_log.assert_has_calls(expected_log_calls)

    @patch.object(sys, 'argv', ['connectz.py', 'illegal_column'])
    @patch('connectz.log')
    def test_illegal_column(self, mocked_log):
        connectz.main()
        expected_log_calls = (call('6'),)
        mocked_log.assert_has_calls(expected_log_calls)

    @patch.object(sys, 'argv', ['connectz.py', 'impossible_game'])
    @patch('connectz.log')
    def test_impossible_game(self, mocked_log):
        connectz.main()
        expected_log_calls = (call('7'),)
        mocked_log.assert_has_calls(expected_log_calls)

    @patch.object(sys, 'argv', ['connectz.py', 'illegal_game'])
    @patch('connectz.log')
    def test_illegal_game(self, mocked_log):
        connectz.main()
        expected_log_calls = (call('8'),)
        mocked_log.assert_has_calls(expected_log_calls)

    @patch.object(sys, 'argv', ['connectz.py', NON_EXISTING_FILE])
    @patch('connectz.log')
    def test_file_error(self, mocked_log):
        connectz.main()
        expected_log_calls = (call('9'),)
        mocked_log.assert_has_calls(expected_log_calls)


if __name__ == '__main__':
    unittest.main()
