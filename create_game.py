import pathlib
import sys


ITERATIONS = 5_000  # 4 rows per iteration


def main():
    moves = ('1\n2\n2\n1\n')
    file_name = sys.argv[1]
    file_path = pathlib.Path.cwd() / 'profilling' / file_name
    with open(file_path, 'w') as file:
        rows = 4 * ITERATIONS
        file.write(f'2 {rows} 3')
        for _ in range(ITERATIONS):
            file.write(moves)
    print(f'File "{file_path}" created with {rows:,} rows')


if __name__ == "__main__":
    main()
