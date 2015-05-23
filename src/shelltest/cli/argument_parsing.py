import pathlib

import argparse


class Result:
    def __init__(self,
                 file_path: pathlib.Path,
                 initial_home_dir_path: pathlib.Path,
                 is_keep_execution_directory_root: bool=False,
                 execution_directory_root_name_prefix: str='shelltest-'):
        self.__file_path = file_path
        self.__initial_home_dir_path = initial_home_dir_path
        self.__is_keep_execution_directory_root = is_keep_execution_directory_root
        self.__execution_directory_root_name_prefix = execution_directory_root_name_prefix

    @property
    def file_path(self) -> pathlib.Path:
        return self.__file_path

    @property
    def initial_home_dir_path(self) -> pathlib.Path:
        return self.__initial_home_dir_path

    @property
    def is_keep_execution_directory_root(self) -> bool:
        return self.__is_keep_execution_directory_root

    @property
    def execution_directory_root_name_prefix(self) -> str:
        return self.__execution_directory_root_name_prefix


def parse(argv: str) -> Result:
    raise NotImplementedError()


def _new_argument_parser() -> argparse.ArgumentParser:
    ret_val = argparse.ArgumentParser(description='Execute Shelltest test case')
    ret_val.add_argument('file',
                         type=str,
                         help='The file containing the test case')
