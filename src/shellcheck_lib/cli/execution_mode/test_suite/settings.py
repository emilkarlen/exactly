import pathlib


class Settings:
    def __init__(self,
                 interpreter: str,
                 suite_root_file_path: pathlib.Path):
        self.__interpreter = interpreter
        self.__suite_root_file_path = suite_root_file_path

    @property
    def interpreter(self) -> str:
        return self.__interpreter

    @property
    def suite_root_file_path(self) -> pathlib.Path:
        return self.__suite_root_file_path
