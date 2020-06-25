import argparse
from collections import namedtuple
import io
import pathlib
import sys


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
            moves = [line.strip() for line in file if line] # TODO: generator?
            return Game(*game_dimensions, moves)
        except:
            raise ValueError('8')


def check_game(content: str) -> str:
    # TODO
    pass


def main():
    try:
        path = input_file()
        content = parse_game(path)
        result = check_game(content)
        log(result)
    except (ValueError, FileNotFoundError) as e:
        log(e.args[0])


if __name__ == '__main__':
    main()
