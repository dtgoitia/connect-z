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

* Finding winning moves. Instead of searching the whole board in each move, the
  current algorithm does the following:

  1. Check if there is any winning/losing game after each move.

  2. Only check the segments of the rows, columns and diagonals which might be
     now -after the last move- potential candidates to contain a winning line.

     These segments are included in the rows, columns and diagonals that cross
     the cell where the last move was done. The length of the segments is
     limited by the cells that -being _n_ the number of cells in the line that
     wins the game- are _n_ cells away from the cell where the last move was
     done. The segments cannot stretch beyond the board limits.

## Others

* Using the `argparse.FileType` type to get the input file was convenient,
  until I tried to pass non existing paths. Capturing the error message
  (`No such file or directory`) required using custom types and it was much
  easier to use a simple validator instead (`validate_file_path`) once the path
  was passed as a string.

* No special logic required for ASCII files as UTF-8 is backwards compatible
  with ASCII [[2][2]].

* This project was entirely built and formatted without any linter, formatter,
  etc. to follow the "third party libraries are not allowed" instruction.

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
