import pathlib
import sys


ITERATIONS = 5_000  # 4 rows per iteration
MOVES = '1\n2\n2\n1\n'

def create_game(file_name, iterations = ITERATIONS, moves = MOVES) -> pathlib.Path:
    path = pathlib.Path.cwd() / 'profilling' / file_name
    with open(path, 'w') as file:
        rows = 4 * iterations
        file.write(f'2 {rows} 3')
        for _ in range(iterations):
            file.write(MOVES)
    print(f'File "{path}" created with {rows:,} rows')
    return path


def main():
    file_name = sys.argv[1]
    create_game(file_name)


if __name__ == "__main__":
    main()
