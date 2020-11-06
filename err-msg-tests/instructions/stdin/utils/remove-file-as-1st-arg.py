import pathlib
import sys

file_path = pathlib.Path(sys.argv[1])

file_path.unlink()
