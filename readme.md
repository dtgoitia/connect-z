Capturing the output from sys was quite unreliable, so I opted for mocking the `log` function.

Using the `argparse.FileType` type was okay, until I passed non existing paths. To capture the `No such file or directory` error I needed to replace it with `validate_file_path`.