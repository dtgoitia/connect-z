Capturing the output from sys was quite unreliable, so I opted for mocking the `log` function.

Using the `argparse.FileType` type was okay, until I passed non existing paths. To capture the `No such file or directory` error I needed to replace it with `validate_file_path`.

I've used a `namedtuple` for `Game` because `dataclass` was still a thing in Python 3.6
The only difference really is performance (`dataclass` is faster to access) and space (`namedtuple` requires less space).
Source: https://stackoverflow.com/questions/51671699/data-classes-vs-typing-namedtuple-primary-use-cases

Generators are preferred over Lists to support huge boards.

Assumption: the input file refers to rows and columns using a 1-based index, not a 0-based one.

The board stores its value in lists because it's more efficient to mutate elements in the lists than copying the whole board by iterating over it and update a single value in the process.

Store board by columns instead of by rows:
  - it is easier to find the first free row in a column, if any
  - no special benefit if I store by rows

Instead of searching the whole board in each move:

  1. Ensure to check if there is any winning/loosing game after each move.

  2. Only check the segments of the rows, columns and diagonals which might be
     now -after the last move- potential candidates to contain a winning line.

     These segments are included in the rows, columns and diagonals that cross
     the cell where the last move was done. The length of the segments is
     limited by the cells that -being N the number of cells in the line that
     wins the game- are N cells away from the cell where the last move was
     done. The segments cannot stretch beyond the board limits.

According to the input file specification "after the game dimensions line, each
subsequent line of the file represents a single move in the game". Hence a file
with empty lines between the moves will result in an invalid game.
