from connectz import Board


def debug(board: Board) -> None:
    """Print the board"""
    plot = ''
    for row in zip(*board.board):
        line = ' '.join([str(cell) for cell in row])
        plot += f'{line}\n'
    print(plot)
