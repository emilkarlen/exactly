import enum
import pathlib

import argparse


class Output(enum.Enum):
    STATUS_CODE = 1
    EXECUTION_DIRECTORY_STRUCTURE_ROOT = 2


class Result:
    def __init__(self,
                 file_path: pathlib.Path,
                 initial_home_dir_path: pathlib.Path,
                 output: Output,
                 is_keep_execution_directory_root: bool=False,
                 execution_directory_root_name_prefix: str='shellcheck-'):
        self.__file_path = file_path
        self.__initial_home_dir_path = initial_home_dir_path
        self.__output = output
        self.__is_keep_execution_directory_root = is_keep_execution_directory_root
        self.__execution_directory_root_name_prefix = execution_directory_root_name_prefix

    @property
    def file_path(self) -> pathlib.Path:
        return self.__file_path

    @property
    def initial_home_dir_path(self) -> pathlib.Path:
        return self.__initial_home_dir_path

    @property
    def output(self) -> Output:
        return self.__output

    @property
    def is_keep_execution_directory_root(self) -> bool:
        return self.__is_keep_execution_directory_root

    @property
    def execution_directory_root_name_prefix(self) -> str:
        return self.__execution_directory_root_name_prefix


def parse(argv: list) -> Result:
    output = Output.STATUS_CODE
    is_keep_execution_directory_root = False
    namespace = _new_argument_parser().parse_args(argv)
    if namespace.print_and_preserve_eds:
        output = Output.EXECUTION_DIRECTORY_STRUCTURE_ROOT
        is_keep_execution_directory_root = True
    return Result(pathlib.Path(namespace.file),
                  pathlib.Path(namespace.file).parent.resolve(),
                  output=output,
                  is_keep_execution_directory_root=is_keep_execution_directory_root)


def _new_argument_parser() -> argparse.ArgumentParser:
    ret_val = argparse.ArgumentParser(description='Execute Shellcheck test case')
    ret_val.add_argument('file',
                         type=str,
                         help='The file containing the test case')
    ret_val.add_argument('--print-and-preserve-eds',
                         default=False,
                         action="store_true",
                         help="""\
                        Execution Directory Structure is preserved,
                        and it's root directory is the only output on stdout.""")
    return ret_val
