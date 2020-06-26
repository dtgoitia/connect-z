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

    @patch.object(sys, 'argv', ['connectz.py', 'player_2_wins_with_row'])
    @patch('connectz.log')
    def test_player_2_wins_with_row(self, mocked_log):
        connectz.main()
        expected_log_calls = (call('2'),)
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
    
    def test_affected_segments(self):
        game = connectz.Game(columns=7, rows=6, line_length=3, moves=())
        board = connectz.Board(game)
        board.board = [
        # row 0  1  2...
            [ 1, 2, 3, 4, 5, 6], # column 0
            [ 7, 8, 9,10,11,12], # column 1
            [13,14,15,16,17,18], # ..
            [19,20,21,22,23,24],
            [25,26,27,28,29,30],
            [31,32,33,34,35,36],
            [37,38,39,40,41,42],
        ]
        board._last_move = connectz.Cell(column=1, row=4)
        segments = [s for s in board._segments_affected_by_last_move()]
        assert segments[0] == (9, 10, 11, 12) # affected column
        assert segments[1] == (5, 11, 17, 23) # affected row
        assert segments[2] == (4, 11, 18)     # affected diagonal a
        assert segments[3] == (21, 16, 11, 6) # affected diagonal b
        
        assert len(segments) == 4


if __name__ == '__main__':
    unittest.main()
