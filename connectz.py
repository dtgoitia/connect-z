import argparse
from collections import namedtuple
from itertools import cycle, islice
import pathlib
from typing import Generator, List, Set
import sys

from pympler import asizeof # TODO: delete

EMPTY_PLACE = 0
PLAYER_A = 1
PLAYER_B = 2


def debug(message: str) -> None:
    # TODO: delete
    print(message)


def log(message: str) -> None:
    # TODO: use loggers to print
    print(message)


def input_file() -> pathlib.PosixPath:
    parser = argparse.ArgumentParser()
    parser.add_argument('inputfilename', nargs='*', type=str)
    args = parser.parse_args()
    files = args.inputfilename

    if len(files) != 1:
        raise ValueError('Provide one input file')

    file = files[0]
    path = pathlib.Path.cwd() / file
    if not path.exists():
        raise FileNotFoundError('9')

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
            raise ValueError('8')


def validate_winnability(game: Game) -> None:
    if (game.line_length <= game.columns or 
        game.line_length <= game.rows):
        return
    raise ValueError('7')


class Board:
    board: List[List[str]]
    line_length: int
    column_amount: int
    row_amount: int

    def __init__(self, game: Game) -> None:
        self.board = [[EMPTY_PLACE for column in range(game.columns)]
                      for row in range(game.rows)]
        self.line_length = game.line_length
        self.column_amount = game.columns
        self.row_amount = game.rows

    def drop_chip(self, player: int, column: int) -> None:
        if self.column_amount < column:
            raise ValueError('6')
        row = self._first_empty_row_by_column(column)
        self.board[row][column] = player

    def status(self) -> int:
        # Where are we? Has anyone won yet?
        # most common win: diagonal, then column, then row
        diagonal_winner = self._check_diagonal_lines()
        if diagonal_winner:
            debug(f'{diagonal_winner} wins with a diagonal line')
            return diagonal_winner

        column_winner = self._check_column_lines()
        if column_winner:
            debug(f'{column_winner} wins with a column line')
            return column_winner

        row_winner = self._check_row_lines()
        if row_winner:
            debug(f'{row_winner} wins with a row line')
            return row_winner
        
        # TODO: how to calculate draw? is there any empty cell?

    @property
    def columns(self) -> Generator[int, None, None]:
        return (column for column in zip(*self.board))

    @property
    def rows(self) -> Generator[Generator[int, None, None], None, None]:
        for row in self.board:
            yield (column for column in row)

    def _check_column_lines(self) -> int:
        # Return 0 if no winner
        # Return 1 if player 1 wins
        # Return 2 if player 2 wins
        pass

    def _check_diagonal_lines(self) -> int:
        # Return 0 if no winner
        # Return 1 if player 1 wins
        # Return 2 if player 2 wins
        pass

    def _check_row_lines(self) -> int:
        # Return 0 if no winner
        # Return 1 if player 1 wins
        # Return 2 if player 2 wins
        winner = 0
        for row in self.rows:
            row = tuple(row)
            # debug(f'Checking {row}')
            for start_column in range(self.column_amount - (self.line_length - 1)):
                end_column = start_column + self.line_length
                # debug(f'columns = {start_column}-{end_column}')
                line = tuple(islice(row, start_column, end_column))
                # debug(f'line: {line}')
                players_involved = set(line)
                if len(players_involved) == 1:
                    winner = players_involved.pop()
                    return winner
    

    def _first_empty_row_by_column(self, column_index: int) -> int:
        column = next(islice(self.columns, column_index, column_index + 1))
        try:
            return column.index(EMPTY_PLACE)
        except ValueError:
            # Column full, impossible to a chip here
            raise ValueError('5')

    def __str__(self) -> str:
        # TODO: for debugging purposes, delete after
        return '\n'.join(' '.join(str(column) for column in row)
                         for row in self.rows)


def play(game: Game) -> str:
    validate_winnability(game)

    game_outcome = None
    # TODO: worth storing all states?
    # only the previous state to see if after the game has been drawn or won,
    # there are still more movevements specified in the input file, case in
    # which you need to throw an excepion

    board = [[0 for row in range(game.rows)] for column in range(game.rows)]
    board = Board(game)
    print(board)
    print('')

    players = cycle((PLAYER_A, PLAYER_B))
    for move, player in zip(game.moves, players):
        debug(f'player {player} drops chip in column {move}')
        column = move - 1
        board.drop_chip(player, column)
        debug(board)
        game_outcome = board.status()
        debug(f'game_outcome={game_outcome}')
        debug('')

    return str(game_outcome)


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
