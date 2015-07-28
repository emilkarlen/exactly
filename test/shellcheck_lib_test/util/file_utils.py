import pathlib


def write_file(path: pathlib.Path, contents: str):
    with open(str(path), 'w') as f:
        f.write(contents)
