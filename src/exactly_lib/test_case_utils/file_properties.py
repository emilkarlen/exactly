import enum
import os
import pathlib
import stat
import types


class FileType(enum.Enum):
    SYMLINK = 0
    REGULAR = 1
    DIRECTORY = 2


class FileTypeInfo:
    def __init__(self,
                 type_argument: str,
                 description: str,
                 stat_mode_predicate: types.FunctionType,
                 pathlib_path_predicate: types.FunctionType):
        self.type_argument = type_argument
        self.pathlib_path_predicate = pathlib_path_predicate
        self.stat_mode_predicate = stat_mode_predicate
        self.description = description


TYPE_INFO = {
    FileType.REGULAR: FileTypeInfo('file', 'regular file', stat.S_ISREG, pathlib.Path.is_file),
    FileType.DIRECTORY: FileTypeInfo('dir', 'directory', stat.S_ISDIR, pathlib.Path.is_dir),
    FileType.SYMLINK: FileTypeInfo('symlink', 'symbolic link', stat.S_ISLNK, pathlib.Path.is_symlink),
}

SYNTAX_TOKEN_2_FILE_TYPE = dict([(info.type_argument, ft) for ft, info in TYPE_INFO.items()])


def lookup_file_type(stat_result) -> FileType:
    """
    :return: None iff the type is an unknown type
    """
    for file_type in TYPE_INFO:
        if TYPE_INFO[file_type].stat_mode_predicate(stat_result.st_mode):
            return file_type
    return None


def stat_results_is_of(file_type: FileType,
                       stat_result) -> bool:
    try:
        return TYPE_INFO[file_type].stat_mode_predicate(stat_result.st_mode)
    except KeyError:
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
    def is_type_of_existing_file(self) -> bool:
        return not self.is_existence

    @property
    def file_exists(self) -> bool:
        return self[1]

    @property
    def type_of_existing_file(self) -> FileType:
        """
        If is_type_of_existing_file gives True,
        then this method gives the related type of file,
        or None if the type is an unknown type
        """
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


def negate_properties(properties_with_neg: PropertiesWithNegation) -> PropertiesWithNegation:
    return PropertiesWithNegation(not properties_with_neg.is_negated,
                                  properties_with_neg.properties)


def negate_result(result: CheckResult) -> CheckResult:
    return CheckResult(not result.is_success,
                       negate_properties(result.cause))


class FilePropertiesCheck:
    def apply(self, path: pathlib.Path) -> CheckResult:
        raise NotImplementedError()


def must_exist(follow_symlinks: bool = True) -> FilePropertiesCheck:
    return _MustExist(follow_symlinks)


def must_exist_as(file_type: FileType,
                  follow_symlinks: bool = True) -> FilePropertiesCheck:
    if follow_symlinks and file_type is FileType.SYMLINK:
        raise ValueError('Cannot follow symlinks when testing for symlink')
    return _MustExistAs(follow_symlinks, file_type)


def negation_of(check: FilePropertiesCheck) -> FilePropertiesCheck:
    return _NegationOf(check)


def render_failure(properties_with_neg: PropertiesWithNegation,
                   file_path: pathlib.Path) -> str:
    failing_property_str = render_failing_property(properties_with_neg)
    return failing_property_str + ': ' + str(file_path)


def render_failing_property(properties_with_neg: PropertiesWithNegation) -> str:
    is_follow_symlinks = properties_with_neg.properties.is_follow_symlinks
    sym_links = 'symbolic links followed' if is_follow_symlinks else 'symbolic links not followed'
    negation = '' if properties_with_neg.is_negated else 'not '

    properties = properties_with_neg.properties
    if properties.is_existence:
        return 'File does {negation}exist ({sym_links})'.format(
            negation=negation,
            sym_links=sym_links)
    else:
        return os.linesep.join(['File is {negation}a {file_type} ({sym_links})'.format(
            negation=negation,
            file_type=TYPE_INFO[properties.type_of_existing_file].description,
            sym_links=sym_links)])


def render_property(properties: Properties) -> str:
    is_follow_symlinks = properties.is_follow_symlinks
    symlink_info = 'symlinks followed' if is_follow_symlinks else 'symlinks not followed'
    if properties.is_existence:
        return 'file does not exist ({symlink_info})'.format(
            symlink_info=symlink_info
        )
    else:
        file_type = properties.type_of_existing_file
        return 'file type is {file_type} ({symlink_info})'.format(
            file_type=file_type.name if file_type else 'unknown',
            symlink_info=symlink_info
        )


class _NegationOf(FilePropertiesCheck):
    def __init__(self, check: FilePropertiesCheck):
        self.__check = check

    def apply(self, path: pathlib.Path) -> CheckResult:
        sub_result = self.__check.apply(path)
        return negate_result(sub_result)


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


class ActualFilePropertiesResolver:
    def __init__(self,
                 expected_file_type: FileType,
                 follow_symlinks: bool = True):
        self._expected_file_type = expected_file_type
        self._follow_symlinks = follow_symlinks

    def resolve_failure_info(self, path: pathlib.Path) -> Properties:
        """
        :return: None iff file has expected properties
        """
        try:
            stat_results = os.stat(str(path),
                                   follow_symlinks=self._follow_symlinks)
            has_expected_type = stat_results_is_of(self._expected_file_type, stat_results)
            if has_expected_type:
                return None
            else:
                return new_properties_for_type_of_existing_file(self._follow_symlinks,
                                                                lookup_file_type(stat_results))
        except FileNotFoundError:
            return new_properties_for_existence(self._follow_symlinks,
                                                False)
