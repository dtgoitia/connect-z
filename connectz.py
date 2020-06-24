import argparse
import sys


def debug(message: str) -> None:
    # TODO: delete
    print(message)

def log(message: str) -> None:
    # TODO: use loggers to print
    print(message)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('inputfilename', nargs='*', type=argparse.FileType('r'),
                        default=None)
    args = parser.parse_args()
    file = args.inputfilename
    # debug(file)
    # import ipdb; ipdb.set_trace()
    if len(file) != 1:
        log('Provide one input file')
        log('Provide one input filex')
        return
    with args.inputfilename as file:
        for line in file:
            log(line)

if __name__ == '__main__':
    main()
