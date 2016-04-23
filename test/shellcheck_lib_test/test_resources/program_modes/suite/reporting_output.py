import pathlib


def suite_begin(file_path: pathlib.Path) -> str:
    return 'SUITE ' + str(file_path) + ': BEGIN'


def suite_end(file_path: pathlib.Path) -> str:
    return 'SUITE ' + str(file_path) + ': END'


def case(file_path: pathlib.Path, status: str) -> str:
    return 'CASE  ' + str(file_path) + ': ' + status
