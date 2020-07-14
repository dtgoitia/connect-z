import enum
import collections
import itertools
import pathlib
import typing
import sys


class Dimensions(typing.NamedTuple):
    columns: int
    rows: int
    line_length: int


class Player(enum.Enum):
    Nobody = 0
    A = 1
    B = 2

    def opponent(self):
        if self is self.Nobody:
            raise ValueError("No opponent if there is no player")
        return self.A if self is self.B else self.B


class Row(int):
    pass


class Column(int):
    pass


class Output(enum.Enum):
    DRAW = 0
    PLAYER_1_WINS = 1
    PLAYER_2_WINS = 2
    INCOMPLETE = 3
    ILLEGAL_CONTINUE = 4
    ILLEGAL_ROW = 5
    ILLEGAL_COLUMN = 6
    ILLEGAL_GAME = 7
    INVALID_FILE = 8
    FILE_ERROR = 9


class Direction(enum.Enum):
    # clockwise naming
    VERTICAL = 0
    DIAGONAL_A = 1
    HORIZONTAL = 2
    DIAGONAL_B = 3


class DirectionStatus:
    player: Player
    n: int  # amount of chips obtained so far to make a winning line
    complete: bool

    def __init__(self, player: Player, n: int, complete: bool):
        self.player = player
        self.n = n
        self.complete = complete


class Move(typing.NamedTuple):
    column: Column
    row: Row
    player: Player


Status = typing.DefaultDict[Direction, DirectionStatus]
Board = typing.DefaultDict[typing.Tuple[Column, Row], Status]


def log(message: typing.Union[int, str]) -> None:
    print(message)


def input_file() -> pathlib.Path:
    arguments = sys.argv[1:]
    if len(arguments) != 1:
        program_file_name = pathlib.Path(__file__).name
        raise ValueError(f"{program_file_name}: Provide one input file")

    file_name = arguments[0]
    path = pathlib.Path.cwd() / file_name
    if not path.exists():
        raise FileNotFoundError(Output.FILE_ERROR.value)

    return path


def parse_dimensions_line(line: str) -> typing.Tuple[int]:
    game_dimensions = line.strip().split(" ")
    if len(game_dimensions) != 3:
        raise ValueError(Output.INVALID_FILE.value)
    return tuple((int(dimension) for dimension in game_dimensions))


def read_input_file(path: pathlib.Path) -> typing.Generator:
    with path.open("r") as file:
        for line in file:
            yield line.strip()


def read_game_dimensions(lines: typing.Iterator) -> Dimensions:
    try:
        first_file_line = next(lines)
    except:
        # file is empty
        raise ValueError(Output.INVALID_FILE.value)

    dimensions = first_file_line.split(" ")
    if len(dimensions) != 3:
        raise ValueError(Output.INVALID_FILE.value)

    columns, rows, line_length = [int(dimension) for dimension in dimensions]
    if columns < line_length and rows < line_length:
        raise ValueError(Output.ILLEGAL_GAME.value)

    return Dimensions(columns, rows, line_length)


def read_moves(dimensions: Dimensions, lines: typing.Iterator) -> typing.Iterator[Move]:
    players = itertools.cycle((Player.A, Player.B))
    columns = collections.defaultdict(int)
    for move, player in zip(lines, players):
        try:
            column = int(move.strip()) - 1  # convert to 0-based index
        except ValueError:
            # the move contains contains a non-numeric value
            raise ValueError(Output.INVALID_FILE.value)
        if column >= dimensions.columns or column < 0:
            raise ValueError(Output.ILLEGAL_COLUMN.value)
        columns[column] += 1
        row = columns[column] - 1  # convert to 0-based index
        if row >= dimensions.rows:
            raise ValueError(Output.ILLEGAL_ROW.value)
        yield Move(column=Column(column), row=Row(row), player=Player(player))


def update_vertical_status_and_check_win(board: Board, dimensions: Dimensions, move: Move) -> bool:
    # get current status of the cell below the move
    if move.row == 0:
        direction_below = DirectionStatus(player=move.player.opponent(), n=0, complete=True)
    else:
        direction_below = board[move.column, move.row - 1][Direction.VERTICAL]

    # generate new status from current state
    if direction_below.player is move.player:
        status = DirectionStatus(player=move.player, n=direction_below.n + 1, complete=True)
    else:
        status = DirectionStatus(player=move.player, n=1, complete=True)

    # update status
    board[move.column, move.row][Direction.VERTICAL] = status

    # check winning condition for new status
    return status.n == dimensions.line_length


def update_horizontal_status_and_check_win(board, dimensions: Dimensions, move: Move) -> bool:
    # get current status
    if move.column == 0:
        # left cell is out of the board
        direction_left = DirectionStatus(player=move.player.opponent(), n=0, complete=True)
    else:
        direction_left = board[move.column - 1, move.row][Direction.HORIZONTAL]

    if move.column + 1 == dimensions.columns:
        # right cell is out of the board
        direction_right = DirectionStatus(player=move.player.opponent(), n=0, complete=True)
    else:
        direction_right = board[move.column + 1, move.row][Direction.HORIZONTAL]

    # generate new status from current state
    if direction_left.player is move.player and direction_right.player is move.player:
        # both sides same player
        status = DirectionStatus(
            player=move.player,
            n=direction_left.n + 1 + direction_right.n,
            complete=direction_left.complete or direction_right.complete,
        )
    elif direction_left.player in (move.player.opponent(), Player.Nobody,) and direction_right.player in (
        move.player.opponent(),
        Player.Nobody,
    ):
        # both sides opponent and/or nobody
        status = DirectionStatus(player=move.player, n=1, complete=True)
    else:
        # one side same player, other side opponent and/or nobody
        status = DirectionStatus(player=move.player, n=direction_left.n + 1 + direction_right.n, complete=True,)

    # update status
    board[move.column, move.row][Direction.HORIZONTAL] = status
    if direction_left.player is move.player:
        # update the farthest cell on the left with the same player
        board[move.column - direction_left.n, move.row][Direction.HORIZONTAL] = status
    if direction_right.player is move.player:
        # update the farthest cell on the right with the same player
        board[move.column + direction_right.n, move.row][Direction.HORIZONTAL] = status

    # check win
    return status.n >= dimensions.line_length


def update_diagonal_a_status_and_check_win(board, dimensions: Dimensions, move: Move) -> bool:
    # get current status
    if move.column == 0:
        # bottom left cell is out of the board
        direction_left = DirectionStatus(player=move.player.opponent(), n=0, complete=True)
    else:
        direction_left = board[move.column - 1, move.row - 1][Direction.DIAGONAL_A]

    if move.column + 1 == dimensions.columns:
        # top right cell is out of the board
        direction_right = DirectionStatus(player=move.player.opponent(), n=0, complete=True)
    else:
        direction_right = board[move.column + 1, move.row + 1][Direction.DIAGONAL_A]

    status_to_check_win = None
    # generate new status from current state
    # same player left
    if direction_left.player is move.player:
        # both sides same player
        if direction_right.player is move.player:
            # both sides same player, left complete
            if direction_left.complete:
                # both sides same player, both sides complete
                if direction_right.complete:
                    # | 1 1 x 1 1 |
                    status_to_check_win = DirectionStatus(player=move.player, n=direction_left.n + 1 + direction_right.n, complete=True)
                # both sides same player, left complete, right incomplete
                else:
                    # | 1 1 x 1 · |
                    status_to_check_win = DirectionStatus(player=move.player, n=direction_left.n + 1 + direction_right.n, complete=True)
                    board[move.column + direction_right.n, move.row + direction_right.n][Direction.DIAGONAL_A] = status_to_check_win
            # both sides same player, left incomplete
            else:
                # both sides same player, left incomplete, right complete
                if direction_right.complete:
                    # | · 1 x 1 1 |
                    status_to_check_win = DirectionStatus(player=move.player, n=direction_left.n + 1 + direction_right.n, complete=True)
                    board[move.column - direction_left.n, move.row - direction_left.n][Direction.DIAGONAL_A] = status_to_check_win
                # both sides same player, both sides incomplete
                else:
                    # | · 1 x 1 · |
                    status_to_check_win = DirectionStatus(player=move.player, n=direction_left.n + 1 + direction_right.n, complete=False)
                    board[move.column + direction_left.n, move.row + direction_left.n][Direction.DIAGONAL_A] = status_to_check_win
                    board[move.column - direction_left.n, move.row - direction_left.n][Direction.DIAGONAL_A] = status_to_check_win
        # left same player, right player opponent/nobody
        else:
            # left same player complete, right player opponent/nobody
            if direction_left.complete:
                # left same player complete, right nobody
                if direction_right.player is Player.Nobody:
                    # | 1 1 x · · |
                    status_to_check_win = DirectionStatus(player=move.player, n=direction_left.n + 1, complete=True)
                    board[move.column, move.row][Direction.DIAGONAL_A] = status_to_check_win
                # left same player complete, right opponent
                else:
                    # | 1 1 x 2 · |
                    status_to_check_win = DirectionStatus(player=move.player, n=direction_left.n + 1, complete=True)
            # left same player incomplete
            else:
                # left same player incomplete, right player opponent/nobody complete
                if direction_right.complete:
                    # left same player incomplete, right player nobody complete
                    if direction_right.player is Player.Nobody:
                        # | · · 1 1 x |
                        status_to_check_win = DirectionStatus(player=move.player, n=direction_left.n + 1, complete=True)
                        board[move.column - direction_left.n, move.row - direction_left.n][Direction.DIAGONAL_A] = status_to_check_win
                    # left same player incomplete, right player opponent complete
                    else:
                        status_to_check_win = DirectionStatus(player=move.player, n=direction_left.n + 1, complete=True)
                        # | · 1 x 2 2 |
                        board[move.column - direction_left.n, move.row - direction_left.n][Direction.DIAGONAL_A] = status_to_check_win
                # left same player incomplete, right player opponent/nobody incomplete
                else:
                    # left same player incomplete, right player nobody incomplete
                    if direction_right.player is Player.Nobody:
                        # | · 1 x · · |
                        status_to_check_win = DirectionStatus(player=move.player, n=direction_left.n + 1, complete=False)
                        board[move.column, move.row][Direction.DIAGONAL_A] = status_to_check_win
                        board[move.column - direction_left.n, move.row - direction_left.n][Direction.DIAGONAL_A] = status_to_check_win
                    # left same player incomplete, right player opponent incomplete
                    else:
                        # | · 1 x 2 · |
                        status_to_check_win = DirectionStatus(player=move.player, n=direction_left.n + 1, complete=True)
                        board[move.column - direction_left.n, move.row - direction_left.n][Direction.DIAGONAL_A] = status_to_check_win
    # opponent/nobody on the left
    else:
        # opponent/nobody left, right same player
        if direction_right.player is move.player:
            # opponent/nobody left complete, right same player
            # TODO: this check is unnecessary, if at the left of the current move there is a board edge or an opponent
            #       then it doesn't matter if left cell is completed or not
            if direction_left.complete:
                # opponent/nobody left complete, right same player complete
                if direction_right.complete:
                    # | 2 2 x 1 1 |
                    # | x 1 1 1 1 |
                    status_to_check_win = DirectionStatus(player=move.player, n=1 + direction_right.n, complete=True)
                # opponent/nobody left complete, right same player incomplete
                else:
                    # | 2 2 x 1 · |
                    # | x 1 · · · |
                    status_to_check_win = DirectionStatus(player=move.player, n=1 + direction_right.n, complete=True)
                    board[move.column + direction_right.n, move.row + direction_right.n][Direction.DIAGONAL_A] = status_to_check_win
            # opponent/nobody left incomplete, right same player
            else:
                # opponent/nobody left incomplete, right same player complete
                if not direction_left.complete:
                    # | · 2 x 1 1 |
                    # | · · x 1 1 |
                    status_to_check_win = DirectionStatus(player=move.player, n=1 + direction_right.n, complete=True)
                    board[move.column, move.row][Direction.DIAGONAL_A] = status_to_check_win
                # opponent/nobody left incomplete, right same player incomplete
                else:
                    # | · 2 x 1 · |
                    # | · · x 1 · |
                    status_to_check_win = DirectionStatus(player=move.player, n=1 + direction_right.n, complete=True)
                    board[move.column, move.row][Direction.DIAGONAL_A] = status_to_check_win
                    board[move.column + direction_right.n, move.row + direction_right.n][Direction.DIAGONAL_A] = status_to_check_win
        # opponent/nobody both sides
        else:
            # opponent/nobody left complete, right opponent/nobody
            if direction_left.complete:
                # opponent/nobody left complete, right opponent/nobody complete
                if direction_right.complete:
                    # | 2 2 x 2 2 |
                    # | 2 2 x |
                    # | x 2 2 |
                    # | x |
                    status_to_check_win = DirectionStatus(player=move.player, n=1, complete=True)
                # opponent/nobody left complete, right opponent/nobody incomplete
                else:
                    # opponent/nobody left complete, right nobody incomplete
                    if direction_right.player is Player.Nobody:
                        # | x · · · · |
                        status_to_check_win = DirectionStatus(player=move.player, n=1, complete=True)
                        board[move.column, move.row][Direction.DIAGONAL_A] = status_to_check_win
                    # opponent/nobody left complete, right opponent incomplete
                    else:
                        # | 2 2 x 2 · |
                        # | x 2 · · · |
                        status_to_check_win = DirectionStatus(player=move.player, n=1, complete=True)
            # opponent/nobody left incomplete, right opponent/nobody
            else:
                # opponent/nobody left incomplete, right opponent/nobody complete
                if direction_right.complete:
                    # nobody left incomplete, right opponent/nobody complete
                    if direction_left.player is Player.Nobody:
                        # | · · x 2 2 |
                        # | · · · · x |
                        status_to_check_win = DirectionStatus(player=move.player, n=1, complete=True)
                        board[move.column, move.row][Direction.DIAGONAL_A] = status_to_check_win
                    # opponent left incomplete, right opponent/nobody complete
                    else:
                        # | · 2 x 2 2 |
                        # | · · · 2 x |
                        status_to_check_win = DirectionStatus(player=move.player, n=1, complete=True)
                # opponent/nobody left incomplete, right opponent/nobody incomplete
                else:
                    # nobody left incomplete, right opponent/nobody incomplete
                    if direction_left.player is Player.Nobody:
                        # nobody left incomplete, right nobody incomplete
                        if direction_right.player is Player.Nobody:
                            # | · · x · · |
                            status_to_check_win = DirectionStatus(player=move.player, n=1, complete=False)
                            board[move.column, move.row][Direction.DIAGONAL_A] = status_to_check_win
                        # nobody left incomplete, right opponent incomplete
                        else:
                            # | · · x 2 · |
                            status_to_check_win = DirectionStatus(player=move.player, n=1, complete=True)
                            board[move.column, move.row][Direction.DIAGONAL_A] = status_to_check_win
                    # opponent left incomplete, right opponent/nobody incomplete
                    else:
                        # opponent left incomplete, right nobody incomplete
                        if direction_right.player is Player.Nobody:
                            # | · 2 x · · |
                            status_to_check_win = DirectionStatus(player=move.player, n=1, complete=True)
                            board[move.column, move.row][Direction.DIAGONAL_A] = status_to_check_win
                        # opponent left incomplete, right opponent incomplete
                        else:
                            # | · 2 x 2 · |
                            status_to_check_win = DirectionStatus(player=move.player, n=1, complete=True)

    # check win
    return status_to_check_win.n >= dimensions.line_length


def update_diagonal_b_status_and_check_win(board: Board, dimensions: Dimensions, move: Move) -> bool:
    # get current status
    if move.column == 0:
        # bottom left cell is out of the board
        direction_left = DirectionStatus(player=move.player.opponent(), n=0, complete=True)
    else:
        direction_left = board[move.column - 1, move.row + 1][Direction.DIAGONAL_B]

    if move.column + 1 == dimensions.columns:
        # top right cell is out of the board
        direction_right = DirectionStatus(player=move.player.opponent(), n=0, complete=True)
    else:
        direction_right = board[move.column + 1, move.row - 1][Direction.DIAGONAL_B]

    status_to_check_win = None
    # generate new status from current state
    # same player left
    if direction_left.player is move.player:
        # both sides same player
        if direction_right.player is move.player:
            # both sides same player, left complete
            if direction_left.complete:
                # both sides same player, both sides complete
                if direction_right.complete:
                    # | 1 1 x 1 1 |
                    status_to_check_win = DirectionStatus(player=move.player, n=direction_left.n + 1 + direction_right.n, complete=True)
                # both sides same player, left complete, right incomplete
                else:
                    # | 1 1 x 1 · |
                    status_to_check_win = DirectionStatus(player=move.player, n=direction_left.n + 1 + direction_right.n, complete=True)
                    board[move.column + direction_right.n, move.row - direction_right.n][Direction.DIAGONAL_B] = status_to_check_win
            # both sides same player, left incomplete
            else:
                # both sides same player, left incomplete, right complete
                if direction_right.complete:
                    # | · 1 x 1 1 |
                    status_to_check_win = DirectionStatus(player=move.player, n=direction_left.n + 1 + direction_right.n, complete=True)
                    board[move.column - direction_left.n, move.row + direction_left.n][Direction.DIAGONAL_B] = status_to_check_win
                # both sides same player, both sides incomplete
                else:
                    # | · 1 x 1 · |
                    status_to_check_win = DirectionStatus(player=move.player, n=direction_left.n + 1 + direction_right.n, complete=False)
                    board[move.column + direction_left.n, move.row - direction_left.n][Direction.DIAGONAL_B] = status_to_check_win
                    board[move.column - direction_left.n, move.row + direction_left.n][Direction.DIAGONAL_B] = status_to_check_win
        # left same player, right player opponent/nobody
        else:
            # left same player complete, right player opponent/nobody
            if direction_left.complete:
                # left same player complete, right nobody
                if direction_right.player is Player.Nobody:
                    # | 1 1 x · · |
                    status_to_check_win = DirectionStatus(player=move.player, n=direction_left.n + 1, complete=True)
                    board[move.column, move.row][Direction.DIAGONAL_B] = status_to_check_win
                # left same player complete, right opponent
                else:
                    # | 1 1 x 2 · |
                    status_to_check_win = DirectionStatus(player=move.player, n=direction_left.n + 1, complete=True)
            # left same player incomplete
            else:
                # left same player incomplete, right player opponent/nobody complete
                if direction_right.complete:
                    # left same player incomplete, right player nobody complete
                    if direction_right.player is Player.Nobody:
                        # | · · 1 1 x |
                        status_to_check_win = DirectionStatus(player=move.player, n=direction_left.n + 1, complete=True)
                        board[move.column - direction_left.n, move.row + direction_left.n][Direction.DIAGONAL_B] = status_to_check_win
                    # left same player incomplete, right player opponent complete
                    else:
                        status_to_check_win = DirectionStatus(player=move.player, n=direction_left.n + 1, complete=True)
                        # | · 1 x 2 2 |
                        board[move.column - direction_left.n, move.row + direction_left.n][Direction.DIAGONAL_B] = status_to_check_win
                # left same player incomplete, right player opponent/nobody incomplete
                else:
                    # left same player incomplete, right player nobody incomplete
                    if direction_right.player is Player.Nobody:
                        # | · 1 x · · |
                        status_to_check_win = DirectionStatus(player=move.player, n=direction_left.n + 1, complete=False)
                        board[move.column, move.row][Direction.DIAGONAL_B] = status_to_check_win
                        board[move.column - direction_left.n, move.row + direction_left.n][Direction.DIAGONAL_B] = status_to_check_win
                    # left same player incomplete, right player opponent incomplete
                    else:
                        # | · 1 x 2 · |
                        status_to_check_win = DirectionStatus(player=move.player, n=direction_left.n + 1, complete=True)
                        board[move.column - direction_left.n, move.row + direction_left.n][Direction.DIAGONAL_B] = status_to_check_win
    # opponent/nobody on the left
    else:
        # opponent/nobody left, right same player
        if direction_right.player is move.player:
            # opponent/nobody left complete, right same player
            # TODO: this check is unnecessary, if at the left of the current move there is a board edge or an opponent
            #       then it doesn't matter if left cell is completed or not
            if direction_left.complete:
                # opponent/nobody left complete, right same player complete
                if direction_right.complete:
                    # | 2 2 x 1 1 |
                    # | x 1 1 1 1 |
                    status_to_check_win = DirectionStatus(player=move.player, n=1 + direction_right.n, complete=True)
                # opponent/nobody left complete, right same player incomplete
                else:
                    # | 2 2 x 1 · |
                    # | x 1 · · · |
                    status_to_check_win = DirectionStatus(player=move.player, n=1 + direction_right.n, complete=True)
                    board[move.column + direction_right.n, move.row - direction_right.n][Direction.DIAGONAL_B] = status_to_check_win
            # opponent/nobody left incomplete, right same player
            else:
                # opponent/nobody left incomplete, right same player complete
                if not direction_left.complete:
                    # | · 2 x 1 1 |
                    # | · · x 1 1 |
                    status_to_check_win = DirectionStatus(player=move.player, n=1 + direction_right.n, complete=True)
                    board[move.column, move.row][Direction.DIAGONAL_B] = status_to_check_win
                # opponent/nobody left incomplete, right same player incomplete
                else:
                    # | · 2 x 1 · |
                    # | · · x 1 · |
                    status_to_check_win = DirectionStatus(player=move.player, n=1 + direction_right.n, complete=True)
                    board[move.column, move.row][Direction.DIAGONAL_B] = status_to_check_win
                    board[move.column + direction_right.n, move.row - direction_right.n][Direction.DIAGONAL_B] = status_to_check_win
        # opponent/nobody both sides
        else:
            # opponent/nobody left complete, right opponent/nobody
            if direction_left.complete:
                # opponent/nobody left complete, right opponent/nobody complete
                if direction_right.complete:
                    # | 2 2 x 2 2 |
                    # | 2 2 x |
                    # | x 2 2 |
                    # | x |
                    status_to_check_win = DirectionStatus(player=move.player, n=1, complete=True)
                # opponent/nobody left complete, right opponent/nobody incomplete
                else:
                    # opponent/nobody left complete, right nobody incomplete
                    if direction_right.player is Player.Nobody:
                        # | x · · · · |
                        status_to_check_win = DirectionStatus(player=move.player, n=1, complete=True)
                        board[move.column, move.row][Direction.DIAGONAL_B] = status_to_check_win
                    # opponent/nobody left complete, right opponent incomplete
                    else:
                        # | 2 2 x 2 · |
                        # | x 2 · · · |
                        status_to_check_win = DirectionStatus(player=move.player, n=1, complete=True)
            # opponent/nobody left incomplete, right opponent/nobody
            else:
                # opponent/nobody left incomplete, right opponent/nobody complete
                if direction_right.complete:
                    # nobody left incomplete, right opponent/nobody complete
                    if direction_left.player is Player.Nobody:
                        # | · · x 2 2 |
                        # | · · · · x |
                        status_to_check_win = DirectionStatus(player=move.player, n=1, complete=True)
                        board[move.column, move.row][Direction.DIAGONAL_B] = status_to_check_win
                    # opponent left incomplete, right opponent/nobody complete
                    else:
                        # | · 2 x 2 2 |
                        # | · · · 2 x |
                        status_to_check_win = DirectionStatus(player=move.player, n=1, complete=True)
                # opponent/nobody left incomplete, right opponent/nobody incomplete
                else:
                    # nobody left incomplete, right opponent/nobody incomplete
                    if direction_left.player is Player.Nobody:
                        # nobody left incomplete, right nobody incomplete
                        if direction_right.player is Player.Nobody:
                            # | · · x · · |
                            status_to_check_win = DirectionStatus(player=move.player, n=1, complete=False)
                            board[move.column, move.row][Direction.DIAGONAL_B] = status_to_check_win
                        # nobody left incomplete, right opponent incomplete
                        else:
                            # | · · x 2 · |
                            status_to_check_win = DirectionStatus(player=move.player, n=1, complete=True)
                            board[move.column, move.row][Direction.DIAGONAL_B] = status_to_check_win
                    # opponent left incomplete, right opponent/nobody incomplete
                    else:
                        # opponent left incomplete, right nobody incomplete
                        if direction_right.player is Player.Nobody:
                            # | · 2 x · · |
                            status_to_check_win = DirectionStatus(player=move.player, n=1, complete=True)
                            board[move.column, move.row][Direction.DIAGONAL_B] = status_to_check_win
                        # opponent left incomplete, right opponent incomplete
                        else:
                            # | · 2 x 2 · |
                            status_to_check_win = DirectionStatus(player=move.player, n=1, complete=True)

    # check win
    return status_to_check_win.n >= dimensions.line_length


def play(dimensions: Dimensions, moves: typing.Iterator[Move]) -> Output:
    winner = Player.Nobody

    def status_creator() -> Status:
        empty_status = DirectionStatus(player=Player.Nobody, n=0, complete=False)
        return collections.defaultdict(lambda: empty_status)

    board: Board = collections.defaultdict(status_creator)

    for move_counter, move in enumerate(moves):
        if winner is not Player.Nobody:
            raise ValueError(Output.ILLEGAL_CONTINUE.value)
        win_checks = (
            update_vertical_status_and_check_win(board, dimensions, move),
            update_horizontal_status_and_check_win(board, dimensions, move),
            update_diagonal_a_status_and_check_win(board, dimensions, move),
            update_diagonal_b_status_and_check_win(board, dimensions, move),
        )
        if True in win_checks:
            winner = move.player

    if winner is Player.Nobody:
        max_moves = dimensions.columns * dimensions.rows
        try:
            if move_counter + 1 == max_moves:
                return Output.DRAW
            return Output.INCOMPLETE
        except UnboundLocalError:
            # Incomplete file with only the dimensions line
            return Output.INCOMPLETE
    elif winner is Player.A:
        return Output.PLAYER_1_WINS
    elif winner is Player.B:
        return Output.PLAYER_2_WINS

    raise Exception("You found a bug...")


def main():
    try:
        path = input_file()
        lines = read_input_file(path)
        dimensions = read_game_dimensions(lines)
        moves = read_moves(dimensions, lines)
        output = play(dimensions, moves)
        log(output.value)
    except (ValueError, FileNotFoundError) as e:
        log(e.args[0])


if __name__ == "__main__":
    main()
