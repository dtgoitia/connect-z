Capturing the output from sys was quite unreliable, so I opted for mocking the `log` function.

Using the `argparse.FileType` type was okay, until I passed non existing paths. To capture the `No such file or directory` error I needed to replace it with `validate_file_path`.

I've used a `namedtuple` for `Game` because `dataclass` was still a thing in Python 3.6
The only difference really is performance (`dataclass` is faster to access) and space (`namedtuple` requires less space).
Source: https://stackoverflow.com/questions/51671699/data-classes-vs-typing-namedtuple-primary-use-cases

Generators are preferred over Lists to support huge boards.

Assumption: the input file refers to rows and columns using a 1-based index, not a 0-based one.

The board stores its value in lists because it's more efficient to mutate elements in the lists than copying the whole board by iterating over it and update a single value in the process.

