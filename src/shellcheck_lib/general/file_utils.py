import os
import pathlib
import tempfile


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


def ensure_parent_directory_does_exist_and_is_a_directory(dst_file_path: pathlib.Path) -> str:
    """
    :return: Failure message if cannot ensure, otherwise None.
    """
    try:
        ensure_parent_directory_does_exist(dst_file_path)
    except NotADirectoryError as ex:
        return 'Not a directory: {}'.format(dst_file_path.parent)


def lines_of(file_path: pathlib.Path) -> list:
    with file_path.open() as f:
        return f.readlines()


def tmp_text_file_containing(contents: str,
                             prefix: str='',
                             suffix: str='',
                             directory=None) -> pathlib.Path:
    fd, absolute_file_path = tempfile.mkstemp(prefix=prefix,
                                              suffix=suffix,
                                              dir=directory,
                                              text=True)
    fo = os.fdopen(fd, 'w+')
    fo.write(contents)
    fo.close()
    return pathlib.Path(absolute_file_path)
