import sys
from time import strftime, localtime

import pathlib
import tempfile
from contextlib import contextmanager
from typing import Callable, List

from exactly_lib import program_info
from exactly_lib.cli.definitions.program_modes.test_case import command_line_options
from exactly_lib.util.file_utils import resolved_path
from exactly_lib_test.test_resources import string_formatting
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


def preprocessor_cli_arg_for_executing_py_file(python_file_name: str) -> str:
    return preprocessor_cli_arg_for_interpret_file(sys.executable,
                                                   python_file_name)


def cli_args_for_executing_py_file(python_file_name: str) -> List[str]:
    return [
        command_line_options.OPTION_FOR_PREPROCESSOR,
        preprocessor_cli_arg_for_executing_py_file(python_file_name),
    ]


def preprocessor_cli_arg_for_interpret_file(interpreter_file_name: str,
                                            source_file_name: str) -> str:
    return (string_formatting.file_name(interpreter_file_name) +
            ' ' +
            string_formatting.file_name(source_file_name)
            )


def cli_args_for_interpret_file(interpreter_file_name: str,
                                source_file_name: str) -> List[str]:
    return [
        command_line_options.OPTION_FOR_PREPROCESSOR,
        preprocessor_cli_arg_for_interpret_file(interpreter_file_name,
                                                source_file_name),
    ]
