import enum
import pathlib


class FileType(enum.Enum):
    SYMLINK = 0
    REGULAR = 1
    DIRECTORY = 2


class FilePropertiesCheck:
    def apply(self, path: pathlib.Path) -> bool:
        raise NotImplementedError()


def must_not_exist() -> FilePropertiesCheck:
    raise NotImplementedError()


def must_exist() -> FilePropertiesCheck:
    raise NotImplementedError()


def must_exist_as(file_type: FileType) -> FilePropertiesCheck:
    raise NotImplementedError()
