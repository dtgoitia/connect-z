import sys
import unittest
from unittest.mock import call, patch

import connectz


EXISTING_FILE = 'good_file'
NON_EXISTING_FILE = 'bad_file'


class Test(unittest.TestCase):

    @patch.object(sys, 'argv', ['connectz.py'])
    @patch('connectz.log')
    def test_no_input_files_provided(self, mocked_log):
        connectz.main()
        expected_log_calls = (
            call('Provide one input file'),
            call('Provide one input filex'),
        )
        mocked_log.assert_has_calls(expected_log_calls)

    @patch.object(sys, 'argv', ['connectz.py', EXISTING_FILE, EXISTING_FILE])
    @patch('connectz.log')
    def test_many_input_files_provided(self, mocked_log):
        connectz.main()
        expected_log_calls = (
            call('Provide one input file'),
            call('Provide one input filex'),
        )
        mocked_log.assert_has_calls(expected_log_calls)


if __name__ == '__main__':
    unittest.main()
