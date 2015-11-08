import enum
import os
import pathlib
import stat


class FileType(enum.Enum):
    SYMLINK = 0
    REGULAR = 1
    DIRECTORY = 2


def stat_results_is_of(file_type: FileType,
                       stat_result) -> bool:
    if file_type is FileType.REGULAR:
        return stat.S_ISREG(stat_result.st_mode)
    elif file_type is FileType.DIRECTORY:
        return stat.S_ISDIR(stat_result.st_mode)
    elif file_type is FileType.SYMLINK:
        return stat.S_ISLNK(stat_result.st_mode)
    raise ValueError('Unknown {}: {}'.format(FileType, file_type))


class FilePropertiesCheck:
    def apply(self, path: pathlib.Path) -> bool:
        raise NotImplementedError()


def must_exist(follow_symlinks: bool=True) -> FilePropertiesCheck:
    return _MustExist(follow_symlinks)


def must_exist_as(file_type: FileType,
                  follow_symlinks: bool=True) -> FilePropertiesCheck:
    if follow_symlinks and file_type is FileType.SYMLINK:
        raise ValueError('Cannot follow symlinks when testing for symlink')
    return _MustExistAs(follow_symlinks, file_type)


def negation_of(check: FilePropertiesCheck):
    return _NegationOf(check)


class _NegationOf(FilePropertiesCheck):
    def __init__(self, check: FilePropertiesCheck):
        self.__check = check

    def apply(self, path: pathlib.Path) -> bool:
        return not self.__check.apply(path)


class _MustExistBase(FilePropertiesCheck):
    def __init__(self, follow_symlinks: bool):
        self.__follow_symlinks = follow_symlinks

    def apply(self, path: pathlib.Path) -> bool:
        try:
            stat_results = os.stat(str(path),
                                   follow_symlinks=self.__follow_symlinks)
            return self._for_existing_file(stat_results)
        except FileNotFoundError:
            return False

    def _for_existing_file(self, stat_results) -> bool:
        raise NotImplementedError()


class _MustExist(_MustExistBase):
    def __init__(self, follow_symlinks: bool):
        super().__init__(follow_symlinks)

    def _for_existing_file(self, stat_results) -> bool:
        return True


class _MustExistAs(_MustExistBase):
    def __init__(self,
                 follow_symlinks: bool,
                 expected_file_type: FileType):
        super().__init__(follow_symlinks)
        self._expected_file_type = expected_file_type

    def _for_existing_file(self, stat_results) -> bool:
        return stat_results_is_of(self._expected_file_type, stat_results)
