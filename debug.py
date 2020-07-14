import connectz


def draw_board(board: connectz.Board, dimensions: connectz.Dimensions) -> None:
    """Print the board"""
    formatted_rows = []
    for row in range(dimensions.rows):
        row = connectz.Row(row)
        row_players = []
        for column in range(dimensions.columns):
            column = connectz.Column(column)
            status = board[column, row]
            directions = list(v for v in status.values() if v.player != connectz.Player.Nobody)
            if not directions:
                player_value = "·"
            else:
                player = directions[0].player
                if player.value == connectz.Player.Nobody.value:
                    player_value = "·"
                else:
                    player_value = player.value
            row_players.append(player_value)
        formatted_row = " ".join([str(player) for player in row_players])
        formatted_rows.append(formatted_row)
    formatted_board = "\n".join(reversed(formatted_rows))
    print(formatted_board)
