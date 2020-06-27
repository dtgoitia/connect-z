import argparse
import enum
from collections import namedtuple
from itertools import cycle, islice
import pathlib
from typing import Generator, List, Set, Tuple, Union
import sys

from pympler import asizeof # TODO: delete

EMPTY_PLACE = 0
PLAYER_A = 1
PLAYER_B = 2
NO_WINNER = 0


class Output(enum.Enum):
    DRAW = 0
    PLAYER_1_WINS = 1
    PLAYER_2_WINS = 2
    INCOMPLETE = 3
    ILLEGAL_CONTINUE = 4
    ILLEGAL_ROW = 5
    ILLEGAL_COLUMN = 6
    ILLEGAL_GAME = 7
    INVALID_FILE = 8
    FILE_ERROR = 9


def debug(message: str) -> None:
    # TODO: delete
    # print(message)
    pass


def log(message: Union[int, str]) -> None:
    # TODO: use loggers to print
    print(message)


def input_file() -> pathlib.PosixPath:
    parser = argparse.ArgumentParser()
    parser.add_argument('inputfilename', nargs='*', type=str)
    args = parser.parse_args()
    files = args.inputfilename

    if len(files) != 1:
        file_name = pathlib.Path(__file__).name
        raise ValueError(f'{file_name}: Provide one input file')

    file = files[0]
    path = pathlib.Path.cwd() / file
    if not path.exists():
        raise FileNotFoundError(Output.FILE_ERROR.value)

    return path


Game = namedtuple('Game', ['columns', 'rows', 'line_length', 'moves'])


def parse_game(path: pathlib.PosixPath) -> Game:
    with open(path, 'r') as file:
        try:
            first_file_line = next(file)
            game_dimensions = first_file_line.strip().split(' ')
            game_dimensions = (int(dimension) for dimension in game_dimensions)
            moves = tuple((int(line) for line in file if line))
            return Game(*game_dimensions, moves)
        except:
            raise ValueError(Output.INVALID_FILE.value)


def validate_winnability(game: Game) -> None:
    if (game.line_length <= game.columns or 
        game.line_length <= game.rows):
        return
    raise ValueError(Output.ILLEGAL_GAME.value)

# TODO: worth having?
Cell = namedtuple('Cell', ['column', 'row'])

class Board:
    board: List[List[str]]
    line_length: int
    column_amount: int
    row_amount: int
    _last_move: Cell

    def __init__(self, game: Game) -> None:
        self.board = [[EMPTY_PLACE for row in range(game.rows)]
                      for column in range(game.columns)]
        self.line_length = game.line_length
        self.column_amount = game.columns
        self.row_amount = game.rows
        self._last_move = None

    def drop_chip(self, player: int, column: int) -> int:
        if self.column_amount < column:
            raise ValueError(Output.ILLEGAL_COLUMN.value)
        row = self._first_empty_row_by_column(column)
        self.board[column][row] = player
        self._last_move = Cell(column=column, row=row)
        return self.status()

    def status(self) -> int:
        segments = self._segments_affected_by_last_move()
        return self._check_winner(segments)

        # TODO: how to calculate draw? is there any empty cell?

    @property
    def columns(self) -> Generator[int, None, None]:
        return (column for column in self.board)

    # Only used for logging the board... TODO: delete
    @property
    def rows(self) -> Generator[int, None, None]:
        return (row for row in zip(*self.board))

    def _segments_affected_by_last_move(self) -> Generator[Tuple[int], None, None]:
        # The status is checked in each iteration, hence is more efficient to
        # check only the cells that could potentially form a winning line with
        # the just updated cell (X), and ignoring any cell that is further than
        # N cells away from X, where N is length of the line to win the game.
        last_column = self._last_move.column
        last_row = self._last_move.row
        distance = self.line_length - 1

        start_column = last_column - distance
        end_column = last_column + distance
        start_row = last_row - distance
        end_row = last_row + distance

        column_range = range(start_column, end_column + 1)
        row_range = range(start_row, end_row)

        column_values = tuple((self.board[last_column][row]
                               for row in row_range
                               if 0 <= row < self.row_amount))
        yield column_values

        row_values = tuple((self.board[column][last_row]
                            for column in column_range
                            if 0 <= column < self.column_amount))
        yield row_values

        diagonal_a = (self.board[column][row]
                      for column, row in zip(column_range, row_range)
                      if 0 <= column < self.column_amount and
                         0 <= row < self.row_amount)
        diagonal_a_values = tuple(diagonal_a)
        yield diagonal_a_values

        reversed_column_range = range(end_column, start_column, -1)
        diagonal_b = (self.board[column][row]
                      for column, row in zip(reversed_column_range, row_range)
                      if 0 <= column < self.column_amount and
                         0 <= row < self.row_amount)
        diagonal_b_values = tuple(diagonal_b)
        yield diagonal_b_values

    def _check_winner(self, segments: Generator[Tuple[int], None, None]) -> int:
        for segment in segments:
            outcome = self._check_winner_in_segment(segment)
            if outcome in (PLAYER_A, PLAYER_B):
                return outcome
        else:
            return NO_WINNER

    def _check_winner_in_segment(self, segment: Tuple[int]) -> int:
        """Return 0 (no winner) or the number representing the winner.

        A segment represents either a row, a column or a diagonal.
        """
        # Optimization
        all_players = set(segment)
        if len(all_players) == 1 and all_players.pop() == EMPTY_PLACE:
            return NO_WINNER

        line = list(segment[:self.line_length - 1])
        remaining_values = segment[self.line_length - 1:]
        for value in remaining_values:
            line.append(value)
            players_in_line = set(line)
            if len(players_in_line) == 1:
                winner = players_in_line.pop()
                if winner == EMPTY_PLACE:
                    continue # TODO: is this correct?
                return winner
            line.pop(0)
        else:
            return NO_WINNER

    def _first_empty_row_by_column(self, column_index: int) -> int:
        column = next(islice(self.columns, column_index, column_index + 1))
        try:
            return column.index(EMPTY_PLACE)
        except ValueError:
            # Column full, impossible to a chip here
            raise ValueError(Output.ILLEGAL_ROW.value)

    def __str__(self) -> str:
        # TODO: for debugging purposes, delete after
        return '\n'.join(' '.join(str(column) for column in row)
                         for row in self.rows)


def play(game: Game) -> int:
    validate_winnability(game)

    outcome = None
    # TODO: worth storing all states?
    # only the previous state to see if after the game has been drawn or won,
    # there are still more movevements specified in the input file, case in
    # which you need to throw an excepion

    board = Board(game)
    debug('')

    players = cycle((PLAYER_A, PLAYER_B))
    for move, player in zip(game.moves, players):
        debug(f'player {player} drops chip in column {move}')
        column = move - 1
        outcome = board.drop_chip(player, column)
        debug('')
        debug(board)
        extra = '' if outcome == 0 else " <-- win"
        debug(f'outcome: {outcome} {extra}')
        debug('')

    return outcome


def main():
    try:
        path = input_file()
        game = parse_game(path)
        outcome = play(game)
        log(outcome)
    except (ValueError, FileNotFoundError) as e:
        log(e.args[0])


if __name__ == '__main__':
    main()
