import enum
import os
import pathlib
import stat


class FileType(enum.Enum):
    SYMLINK = 0
    REGULAR = 1
    DIRECTORY = 2


type_name = {
    FileType.REGULAR: 'regular file',
    FileType.DIRECTORY: 'directory',
    FileType.SYMLINK: 'symbolic link',
}


def stat_results_is_of(file_type: FileType,
                       stat_result) -> bool:
    if file_type is FileType.REGULAR:
        return stat.S_ISREG(stat_result.st_mode)
    elif file_type is FileType.DIRECTORY:
        return stat.S_ISDIR(stat_result.st_mode)
    elif file_type is FileType.SYMLINK:
        return stat.S_ISLNK(stat_result.st_mode)
    raise ValueError('Unknown {}: {}'.format(FileType, file_type))


class Properties(tuple):
    def __new__(cls,
                follow_symlinks: bool,
                file_exists: bool,
                type_of_existing_file: FileType):
        return tuple.__new__(cls, (follow_symlinks, file_exists, type_of_existing_file))

    @property
    def is_follow_symlinks(self) -> bool:
        return self[0]

    @property
    def is_existence(self) -> bool:
        return self[1] is not None

    @property
    def is_type_of_existing_file(self) -> FileType:
        return not self.is_existence

    @property
    def file_exists(self) -> bool:
        return self[1]

    @property
    def type_of_existing_file(self) -> FileType:
        return self[2]


def new_properties_for_existence(follow_symlinks: bool,
                                 file_exists: bool) -> Properties:
    return Properties(follow_symlinks, file_exists, None)


def new_properties_for_type_of_existing_file(follow_symlinks: bool,
                                             type_of_existing_file: FileType) -> Properties:
    return Properties(follow_symlinks, None, type_of_existing_file)


class PropertiesWithNegation(tuple):
    def __new__(cls,
                is_negated: bool,
                properties: Properties):
        return tuple.__new__(cls, (is_negated, properties,))

    @property
    def is_negated(self) -> bool:
        return self[0]

    @property
    def properties(self) -> Properties:
        return self[1]


class CheckResult(tuple):
    def __new__(cls,
                is_success: bool,
                cause: PropertiesWithNegation):
        return tuple.__new__(cls, (is_success, cause,))

    @property
    def is_success(self) -> bool:
        return self[0]

    @property
    def cause(self) -> PropertiesWithNegation:
        return self[1]


def negate(result: CheckResult) -> CheckResult:
    return CheckResult(not result.is_success,
                       result.cause)


class FilePropertiesCheck:
    def apply(self, path: pathlib.Path) -> CheckResult:
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


def render_failure(properties_with_neg: PropertiesWithNegation.properties,
                   file_path: pathlib.Path) -> str:
    is_follow_symlinks = properties_with_neg.properties.is_follow_symlinks
    sym_links = 'symbolic links followed' if is_follow_symlinks else 'symbolic links not followed'
    properties = properties_with_neg.properties
    if properties_with_neg.is_negated:
        if properties.is_existence:
            return 'File does exist ({}): {}'.format(sym_links, str(file_path))
        else:
            return os.linesep.join(['File is a {} ({}):'.format(type_name[properties.type_of_existing_file],
                                                                sym_links),
                                    str(file_path)])
    else:
        if properties.is_existence:
            return 'File does not exist ({}):{}'.format(sym_links, str(file_path))
        else:
            return os.linesep.join(['File is not a {} ({}):'.format(type_name[properties.type_of_existing_file],
                                                                    sym_links),
                                    str(file_path)])


class _NegationOf(FilePropertiesCheck):
    def __init__(self, check: FilePropertiesCheck):
        self.__check = check

    def apply(self, path: pathlib.Path) -> CheckResult:
        sub_result = self.__check.apply(path)
        return negate(sub_result)


class _MustExistBase(FilePropertiesCheck):
    def __init__(self, follow_symlinks: bool):
        self._follow_symlinks = follow_symlinks

    def apply(self, path: pathlib.Path) -> CheckResult:
        try:
            stat_results = os.stat(str(path),
                                   follow_symlinks=self._follow_symlinks)
            return self._for_existing_file(stat_results)
        except FileNotFoundError:
            return CheckResult(False,
                               PropertiesWithNegation(False,
                                                      new_properties_for_existence(self._follow_symlinks,
                                                                                   False)))

    def _for_existing_file(self, stat_results) -> CheckResult:
        raise NotImplementedError()


class _MustExist(_MustExistBase):
    def __init__(self, follow_symlinks: bool):
        super().__init__(follow_symlinks)

    def _for_existing_file(self, stat_results) -> CheckResult:
        return CheckResult(True,
                           PropertiesWithNegation(False,
                                                  new_properties_for_existence(self._follow_symlinks,
                                                                               True)))


class _MustExistAs(_MustExistBase):
    def __init__(self,
                 follow_symlinks: bool,
                 expected_file_type: FileType):
        super().__init__(follow_symlinks)
        self._expected_file_type = expected_file_type

    def _for_existing_file(self, stat_results) -> CheckResult:
        result = stat_results_is_of(self._expected_file_type, stat_results)
        return CheckResult(result,
                           PropertiesWithNegation(False,
                                                  new_properties_for_type_of_existing_file(self._follow_symlinks,
                                                                                           self._expected_file_type)))
