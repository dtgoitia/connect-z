import argparse
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


def validate_file_content(content: str) -> None:
    # TODO
    raise ValueError('8')


def read_content(path: pathlib.PosixPath) -> str:
    # TODO: igual mergealo con el input_file de arriba?
    with open(path, 'r') as file:
        content = file.read()
    validate_file_content(content)
    return content


def check_game(content: str) -> str:
    # TODO
    pass


def main():
    try:
        path = input_file()
        content = read_content(path)
        result = check_game(content)
        log(result)
    except (ValueError, FileNotFoundError) as e:
        log(e.args[0])


if __name__ == '__main__':
    main()
