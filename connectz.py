import argparse

# TODO: use loggers to print
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('inputfilename', nargs='?', type=argparse.FileType('r'),
                        default=None)
    # import ipdb; ipdb.set_trace()
    args = parser.parse_args()
    print(args)
    with args.inputfilename as file:
        for line in file:
            print(line)

if __name__ == '__main__':
    main()
