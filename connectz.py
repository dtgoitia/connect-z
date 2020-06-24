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
    import ipdb; ipdb.set_trace()
    if not path.exists():
        raise FileNotFoundError('9')

    return files[0]


def main():
    try:
        file = input_file()
    except (ValueError, FileNotFoundError) as e:
        log(e.args[0])
        return

    with file:
        for line in file:
            log(line)


if __name__ == '__main__':
    main()
