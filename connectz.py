import argparse
from collections import namedtuple
from itertools import cycle, islice
import pathlib
from typing import Generator, List, Set
import sys


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

    def __init__(self, game: Game) -> None:
        self.column_amount = game.columns
        self.row_amount = game.rows
        self.board = [[EMPTY_PLACE for column in range(game.columns)]
                      for row in range(game.rows)]

    def drop_chip(self, player: int, column: int) -> None:
        row = self._first_empty_row_by_column(column)
        self.board[row][column] = player

    def status(self) -> int:
        # Where are we? Has anyone won yet?
        pass

    @property
    def columns(self) -> Generator[int, None, None]:
        return (column for column in zip(*self.board))

    @property
    def rows(self) -> Generator[Generator[int, None, None], None, None]:
        for row in self.board:
            yield (column for column in row)
    
    def _first_empty_row_by_column(self, column_index: int) -> int:
        column = next(islice(self.columns, column_index, column_index + 1))
        for row_index, value in enumerate(column):
            if value == EMPTY_PLACE:
                return row_index
        else:
            # TODO: if column is full, handle it
            raise ValueError('??')

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
        print(f'player {player} drops chip in column {move}')
        column = move - 1
        board.drop_chip(player, column)
        print(board)
        print('')

    return game_outcome


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
