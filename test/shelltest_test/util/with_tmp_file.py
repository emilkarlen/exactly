from contextlib import contextmanager
import os
import pathlib
import tempfile


@contextmanager
def tmp_file_containing(contents: str,
                        suffix: str='') -> pathlib.Path:
    """
    Returns a context manager (used by with tmp_file(...) as file_path) ...
    The context manager takes care of deleting the file.

    :param contents: The contents of the returned file.
    :param suffix: A possible suffix of the file name (a dot does not automatically separate stem, suffix).
    :return: File path of a closed text file with the given contents.
    """
    path = None
    try:
        fd, absolute_file_path = tempfile.mkstemp(prefix='shelltest-test-',
                                                  suffix=suffix,
                                                  text=True)
        fo = os.fdopen(fd, "w+")
        fo.write(contents)
        fo.close()
        path = pathlib.Path(absolute_file_path)
        yield path
    finally:
        if path:
            path.unlink()


def tmp_file_containing_lines(content_lines: list,
                              suffix: str='') -> pathlib.Path:
    """
    Short cut to tmp_file_containing combined with giving the contents as a string of lines.
    """
    contents = os.linesep.join(content_lines) + os.linesep
    return tmp_file_containing(contents,
                               suffix=suffix)
