import pathlib
import sys

file_path = pathlib.Path(sys.argv[1])

result = (
    0
    if file_path.is_file()
    else
    1
)

sys.exit(result)
