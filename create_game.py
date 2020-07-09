import itertools
import math
import pathlib
import sys


def move_generator(columns: int, rows: int, line_length: int):
    if line_length < 3:
        raise ValueError(f'line length must be 3 or bigger')

    # columns: 1 2 3 4     move sequence:
    # row 1:   A A B B     1 3 2 4
    # row 2:   B B A A     6 8 5 7
    basic_block = [1, 3, 2, 4, 3, 1, 4, 2]
    block_length = 4
    block_height = 2

    # how many basic blocks fit in the board considering the column amount
    h_size = math.floor(columns / block_length)

    # how many basic blocks fit in the board considering the row amount
    v_size = math.floor(rows / block_height)

    def block_generator(start_column: int):
        relocated_block = (column + start_column for column in basic_block)
        return relocated_block

    start_columns = range(0, columns - block_length + 1, block_length)
    start_rows = range(0, rows - block_height + 1, block_height)
    
    for start_row in start_rows:
        for start_column in start_columns:
            for move in block_generator(start_column):
                yield move


def create_game(file_name, *, columns, rows, line_length) -> pathlib.Path:
    path = pathlib.Path.cwd() / 'profilling' / file_name
    with open(path, 'w') as file:
        file.write(f'{columns} {rows} {line_length}\n')
        for i, move in enumerate(move_generator(columns, rows, line_length)):
            file.write(f'{move}\n')
    print(f'File "{path}" created with {i:,} moves')
    return path


def main():
    file_name = sys.argv[1]
    n = sys.argv[2]
    create_game(file_name, columns=n, rows=n, line_length=n)


if __name__ == "__main__":
    main()
