# Observations and considerations

## Assumptions

* The input file refers to rows and columns using a 1-based index, instead of a
  0-based index.

* According to the input file specification "after the game dimensions line,
  each subsequent line of the file represents a single move in the game".
  Hence a file with empty lines between the moves will result in an invalid
  game.

* According to the instructions "a move is described by a single positive
  integer", which is unclear about whether an input file might have negative
  integers or zero, so I decided to code defensively and check each move to
  discard invalid ranges.

## Performance

* `namedtuple` vs `dataclass` vs `dict`: `dataclass` was added in Python 3.7,
  so in order to improve readability `namedtuple` was my best second option.
  The main difference is performance (being `dataclass` faster to access), and
  space (`namedtuple` requires less memory) [[1][1]]. However, at the end of
  the exercise, while optimizing the code, I realised that the `namedtuple` was
  adding little value compared to a `dict` in terms of readability so I decided
  to replace `namedtuple`s for `dict`s where access was frequent.

* Generators are preferred over Sequences to keep memory low when possible. I
  started applying them on the board (see first commits), but then I realised
  that it was faster to mutate 1 item in a massive list than iterating over the
  same massive list and replacing it on the fly with generators. Also, the
  second approach was not easy to read nor reason.

* I initially modelled the board by-rows, because at that moment I was thinking
  about brute-force checking every row and column for a given board state in
  order to find a winner. In this scenario, the first rows were more likely to
  get populated and therefore more likely to find a winning line in them. This
  is why it seemed a good idea to iterate over rows, instead of iterating over
  columns.
  
  Then I came up with the ~~happy idea~~ algorithm that I have implemented
  which requires considerably less checks per move, so there was now no
  incentive to preserve the 'by-rows' approach (see next point). Besides,
  switching to a 'by-columns' approach made it easier to find the first free
  row in a given column, which is a huge benefit. 

* Finding winning moves. The latest algorithm works as follows:

  - The board stores 4 overlapped states: 1 state per type of line -vertical,
    horizontal and diagonals.

  - Each cell in each state tracks:

    1. Line length achieved so far (`n`): integer that describes how many chips
    in a row of the same player are next to a given cell.

    2. Completeness: boolean value that describes the cell is complete when one
    of its adjacent cells cannot grow further in that direction.
    
    Example: analysing rows, imagine that the cell where the player 1 drops the
    chip (x) has another 3 chips of the same player (1) to the right and the
    player 2 has another chip (2) just after:
    
    ```
    | · · 2 1 1 1 x · |
    ```

    where:

      - `|`: board edge 

      - `·`: empty space

      - `x`: dropped chip (belongs to player 1)

      - `1`: player 1 chips

      - `2`: player 2 chips

    In this line, once the player 1 drops its chip, all player 1 chips will
    have an `n` of 4. All player 1 chips will be completed too, because the
    line cannot grow towards the left, as there is a player 2 chip blocking
    that direction of progress for the player 1.

  - When a chip is dropped in a cell, only the nearest 2 cells need to be
    checked per line type (vertical/horizontal/diagonal) in order to determine
    if there is a winning line. If there is not a winning move, only 3 cells
    might need updating:

      - Cell where the chip was dropped in the last move.

      - Cell at the left end: this is the furthest cell in a given direction,
        assuming all cells in between belong to the same player. This cell is
        easy to find as the cell immediately adjacent to the last move tells us
        how many cells away is with the `n` value.

  - Main benefit: constant time complexity to check winning moves, regardless
    of the line size or board size.

## Others

* ~~Using the `argparse.FileType` type to get the input file was convenient,
  until I tried to pass non existing paths. Capturing the error message
  (`No such file or directory`) required using custom types and it was much
  easier to use a simple validator instead (`validate_file_path`) once the path
  was passed as a string.~~ Using `sys.argv` is simpler and cleaner.

* No special logic required for ASCII files as UTF-8 is backwards compatible
  with ASCII [[2][2]].

* This project was entirely built and formatted without any linter,
  ~~formatter~~, etc. to follow the "third party libraries are not allowed"
  instruction. `black` was used to speed up formatting during the last
  refactor.

* This project has been run and tested with Python 3.6.9.

## Testing observations

* Given the small size of this program, I have favoured integration functional
  tests over unit-tests because:

    1. I was foreseeing a refactor once all the acceptance criteria were met.
       This actually happened.
    2. The cost of running "heavier" high-level integration tests was
       negligible due to the reduced amount of tests.

* Capturing the `stdout` from `sys` was quite unreliable, so I opted for
  mocking the `log` function. Using `subprocess.Popen` to execute each test
  would allow me to capture the `stdout` but then I would loose the ability to
  debug my code with `ipdb`.

* Pretty much the whole exercise was developed in a TDD fashion due to the lack
  of time, sufficiently detailed acceptance criteria and high probability of
  refactor/optimization after first working implementation.

## External references

\[1] [StackOverflow. Data Classes vs typing.NamedTuple primary use cases][1]

\[2] [Python Docs. Unicode][2]

[1]: https://stackoverflow.com/questions/51671699/data-classes-vs-typing-namedtuple-primary-use-cases
[2]: https://docs.python.org/3/howto/unicode.html
