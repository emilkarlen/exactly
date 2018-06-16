import pathlib
import tempfile
from contextlib import contextmanager
from time import strftime, localtime
from typing import Callable

from exactly_lib import program_info
from exactly_lib.util.file_utils import resolved_path
from exactly_lib_test.test_resources.files.file_structure import DirContents


@contextmanager
def dir_contents_and_preprocessor_source(
        dir_contents__given_preprocessor_file_path: Callable[[pathlib.Path], DirContents],
        preprocessor_py_source: str):
    """
    :param dir_contents__given_preprocessor_file_path: pathlib.Path -> DirContents
    A function that given the path of the file that contains the preprocessor, gives
    a DirContents.  This DirContents is then written by this method to
    a new tmp directory.
    A contextmanager that gives a pair of pathlib.Path:s:
    The first one is the root directory that contains the structure given
    by dir_contents.
    The other is the file that contains preprocessor_py_source.

    The preprocessor source file is guarantied to not be located inside
      the first directory.
    (test-case-file-path, preprocessor-source-file).
   """
    prefix = strftime(program_info.PROGRAM_NAME + '-test-', localtime())
    with tempfile.TemporaryDirectory(prefix=prefix + '-preprocessor-') as pre_proc_dir:
        preprocessor_file_path = resolved_path(pre_proc_dir) / 'preprocessor.py'
        with preprocessor_file_path.open('w') as f:
            f.write(preprocessor_py_source)
        dir_contents = dir_contents__given_preprocessor_file_path(preprocessor_file_path)
        with tempfile.TemporaryDirectory(prefix=prefix + '-dir-contents-') as dir_contents_root:
            dir_contents_dir_path = resolved_path(dir_contents_root)
            dir_contents.write_to(dir_contents_dir_path)
            yield (dir_contents_dir_path, preprocessor_file_path)
