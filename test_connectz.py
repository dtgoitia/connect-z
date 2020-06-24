import io
import sys
import unittest
from unittest.mock import MagicMock, patch

from connectz import main


class Test(unittest.TestCase):

    @patch.object(sys, 'argv', ['connectz.py', 'good_file'])
    def test_no_input_files_provided(self):
        main()

    # def test_many_input_files_provided(self):
    #     self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
