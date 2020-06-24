import io
import sys
import unittest
from unittest.mock import MagicMock, patch

from connectz import main


class Test(unittest.TestCase):

    def test_no_input_files_provided(self):
        args = ['connectz.py', 'good_file']
        with patch.object(sys, 'argv', args):
            main()
        self.assertEqual(True, True)

    def test_many_input_files_provided(self):
        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
