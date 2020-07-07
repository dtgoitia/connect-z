import argparse
import enum
from collections import namedtuple
from itertools import cycle
import pathlib
from typing import Dict, Generator, List, Set, Tuple, Union


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


def log(message: Union[int, str]) -> None:
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


Dimensions = namedtuple('Dimensions', ['columns', 'rows', 'line_length'])


def parse_dimensions_line(line: str) -> Tuple[int]:
    game_dimensions = line.rstrip().split(' ')
    if len(game_dimensions) != 3:
        raise ValueError(Output.INVALID_FILE.value)
    return tuple((int(dimension) for dimension in game_dimensions)) 


def parse_game(path: pathlib.PosixPath) -> Generator:
    with open(path, 'r') as file:
        try:
            first_file_line = next(file)
        except:
            # file is empty
            raise ValueError(Output.INVALID_FILE.value)

        dimensions = first_file_line.rstrip().split(' ')
        if len(dimensions) != 3:
            raise ValueError(Output.INVALID_FILE.value)

        dimensions = (int(dimension) for dimension in dimensions)
        yield Dimensions(*dimensions)

        for move in file:
            try:
                yield int(move.rstrip())
            except ValueError:
                # the move contains contains a non-numeric value
                raise ValueError(Output.INVALID_FILE.value)


def validate_winnability(dimensions: Dimensions) -> None:
    if (dimensions.line_length <= dimensions.columns or 
        dimensions.line_length <= dimensions.rows):
        return
    raise ValueError(Output.ILLEGAL_GAME.value)


class Board:
    board: List[List[str]]
    line_length: int
    column_amount: int
    row_amount: int
    _last_move: Dict[str, str]

    __slots__ = ['board', 'line_length', 'column_amount', 'row_amount',
                 '_last_move']
 
    def __init__(self, dimensions: Dimensions) -> None:
        # The row that contains the columns never mutates, hence it can be a 
        # tuple to speed up data retrieval.
        # The columns, however, will mutate and therefore need to be lists.
        self.board = tuple([EMPTY_PLACE for row in range(dimensions.rows)]
                           for column in range(dimensions.columns))
                           # TODO: think how can you add chips on the go, and
                           # check efficiently if the column is full, etc.
        self.line_length = dimensions.line_length
        self.column_amount = dimensions.columns
        self.row_amount = dimensions.rows
        self._last_move = None

    def drop_chip(self, player: int, column: int) -> int:
        if column < 0 or self.column_amount <= column:
            raise ValueError(Output.ILLEGAL_COLUMN.value)
        row = self._first_empty_row_by_column(column)
        self.board[column][row] = player
        self._last_move = {'column': column, 'row': row}
        return self.status()

    def status(self) -> int:
        segments = self._segments_affected_by_last_move()
        return self._check_winner(segments)

    def _check_winner(self, segments: Generator[Tuple[int], None, None]) -> int:
        for segment in segments:
            outcome = self._check_winner_in_segment(segment)
            if outcome != NO_WINNER:
                return outcome
        else:
            return NO_WINNER

    def _check_winner_in_segment(self, segment: Tuple[int]) -> int:
        """Return 0 (no winner) or the number representing the winner.

        A segment represents a subset of a row, a column or a diagonal.

        Assumption: all segments passed to this method will always include the
        cell where the last chip was dropped.
        """
        for i in range(0, len(segment) - (self.line_length - 1)):
            line = segment[i:i + self.line_length]
            if EMPTY_PLACE in line:
                continue

            if PLAYER_A in line:
                if PLAYER_B in line:
                    continue
                return PLAYER_A
            else:
                return PLAYER_B
        else:
            return NO_WINNER

    def _first_empty_row_by_column(self, column_index: int) -> int:
        try:
            return self.board[column_index].index(EMPTY_PLACE)
        except ValueError:
            # Column full, impossible to a chip here
            raise ValueError(Output.ILLEGAL_ROW.value)

    def _segments_affected_by_last_move(self) -> Generator[Tuple[int], None, None]:
        # The status is checked in each iteration, hence is more efficient to
        # check only the cells that could potentially form a winning line with
        # the just updated cell (X), and ignoring any cell that is further than
        # N cells away from X, where N is length of the line to win the game.
        last_column = self._last_move['column']
        last_row = self._last_move['row']
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


def play(dimensions: Dimensions, moves: Generator) -> int:
    winner, outcome = None, None
    board = Board(dimensions)

    players = cycle((PLAYER_A, PLAYER_B))
    for move_counter, (move, player) in enumerate(zip(moves, players)):
        column = move - 1 # translate from 1-based to 0-based index
        outcome = board.drop_chip(player, column)
        if outcome != NO_WINNER:
            if winner:
                raise ValueError(Output.ILLEGAL_CONTINUE.value)
            winner = outcome
    
    if outcome is None:
        # No moves in the input file, only game dimensions
        return Output.INCOMPLETE.value

    if outcome == NO_WINNER:
        max_moves = dimensions.columns * dimensions.rows
        if move_counter + 1 == max_moves:
            # All board is full, but no winner
            return Output.DRAW.value
        # All moves consumed, but no winner
        return Output.INCOMPLETE.value
    return outcome


def main():
    try:
        path = input_file()
        parsed_game = parse_game(path)

        dimensions = next(parsed_game)
        validate_winnability(dimensions)

        outcome = play(dimensions, parsed_game)
        log(outcome)
    except (ValueError, FileNotFoundError) as e:
        log(e.args[0])


if __name__ == '__main__':
    main()
