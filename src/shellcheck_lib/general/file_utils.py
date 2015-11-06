import pathlib


def write_new_text_file(file_path: pathlib.Path,
                        contents: str):
    """
    Fails if the file already exists.
    """
    with file_path.open('x') as f:
        f.write(contents)


def ensure_parent_directory_does_exist(dst_file_path: pathlib.Path):
    containing_dir_path = dst_file_path.parent
    if not containing_dir_path.exists():
        containing_dir_path.mkdir(parents=True)


def lines_of(file_path: pathlib.Path) -> list:
    with file_path.open() as f:
        return f.readlines()
