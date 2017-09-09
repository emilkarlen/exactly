import pathlib

from exactly_lib.test_case_utils import file_properties
from exactly_lib.type_system.logic.file_matcher import FileMatcher
from exactly_lib.util import dir_contents_selection


class FileMatcherFromSelectors(FileMatcher):
    """Selects files from a directory according the a file condition."""

    def __init__(self, selectors: dir_contents_selection.Selectors):
        self._selectors = selectors

    @property
    def option_description(self) -> str:
        return 'selectors - this class should be removes'

    @property
    def selectors(self) -> dir_contents_selection.Selectors:
        return self._selectors

    def matches(self, path: pathlib.Path) -> bool:
        raise NotImplementedError('this method should never be used, since this class should be refactored away')


class FileMatcherConstant(FileMatcher):
    """Selects files from a directory according the a file condition."""

    def __init__(self, result: bool):
        self._result = result

    @property
    def result_constant(self) -> bool:
        return self._result

    @property
    def option_description(self) -> str:
        return 'any file' if self._result else 'no file'

    def matches(self, path: pathlib.Path) -> bool:
        return self._result


class FileMatcherNameGlobPattern(FileMatcher):
    """Matches the name (whole path, not just base name) of a path on a shell glob pattern."""

    def __init__(self, glob_pattern: str):
        self._glob_pattern = glob_pattern

    @property
    def glob_pattern(self) -> str:
        return self._glob_pattern

    @property
    def option_description(self) -> str:
        return 'name matches glob pattern ' + self._glob_pattern

    def matches(self, path: pathlib.Path) -> bool:
        return path.match(self._glob_pattern)


class FileMatcherType(FileMatcher):
    """Matches the type of file."""

    def __init__(self, file_type: file_properties.FileType):
        self._file_type = file_type
        self._pathlib_predicate = file_properties.TYPE_INFO[self._file_type].pathlib_path_predicate

    @property
    def file_type(self) -> file_properties.FileType:
        return self._file_type

    @property
    def option_description(self) -> str:
        return 'type is ' + file_properties.TYPE_INFO[self._file_type].description

    def matches(self, path: pathlib.Path) -> bool:
        return self._pathlib_predicate(path)


class FileMatcherNot(FileMatcher):
    """Matcher that negates a given matcher."""

    def __init__(self, matcher: FileMatcher):
        self._matcher = matcher

    @property
    def negated_matcher(self) -> FileMatcher:
        return self._matcher

    @property
    def option_description(self) -> str:
        return self._matcher.option_description

    def matches(self, path: pathlib.Path) -> bool:
        return not self._matcher.matches(path)


class FileMatcherAnd(FileMatcher):
    """Matcher that and:s a list of matchers."""

    def __init__(self, matchers: list):
        self._matchers = tuple(matchers)

    @property
    def matchers(self) -> list:
        return list(self._matchers)

    @property
    def option_description(self) -> str:
        return '({})'.format(','.join(map(lambda fm: fm.option_description, self.matchers)))

    def matches(self, path: pathlib.Path) -> bool:
        return all([matcher.matches(path)
                    for matcher in self._matchers])


class FileMatcherOr(FileMatcher):
    """Matcher that or:s a list of matchers."""

    def __init__(self, matchers: list):
        self._matchers = tuple(matchers)

    @property
    def option_description(self) -> str:
        return '({})'.format(','.join(map(lambda fm: fm.option_description, self.matchers)))

    @property
    def matchers(self) -> list:
        return list(self._matchers)

    def matches(self, path: pathlib.Path) -> bool:
        return any([matcher.matches(path)
                    for matcher in self._matchers])


MATCH_EVERY_FILE = FileMatcherConstant(True)


class FileMatcherStructureVisitor:
    """
    Visits all variants of :class:`FileMatcher`.

    The existence of this class means that the structure of :class:`FileMatcher`s
    is fixed. The reason for this is to, among other things, support optimizations
    of selectors.
    """

    def visit(self, matcher: FileMatcher):
        if isinstance(matcher, FileMatcherFromSelectors):
            return self.visit_selectors(matcher)
        if isinstance(matcher, FileMatcherNameGlobPattern):
            return self.visit_name_glob_pattern(matcher)
        if isinstance(matcher, FileMatcherType):
            return self.visit_type(matcher)
        if isinstance(matcher, FileMatcherNot):
            return self.visit_not(matcher)
        if isinstance(matcher, FileMatcherAnd):
            return self.visit_and(matcher)
        if isinstance(matcher, FileMatcherOr):
            return self.visit_or(matcher)
        if isinstance(matcher, FileMatcherConstant):
            return self.visit_constant(matcher)
        else:
            raise TypeError('Unknown {}: {}'.format(FileMatcher,
                                                    str(matcher)))

    def visit_constant(self, matcher: FileMatcherConstant):
        raise NotImplementedError('abstract method')

    def visit_name_glob_pattern(self, matcher: FileMatcherNameGlobPattern):
        raise NotImplementedError('abstract method')

    def visit_type(self, matcher: FileMatcherType):
        raise NotImplementedError('abstract method')

    def visit_not(self, matcher: FileMatcherNot):
        raise NotImplementedError('abstract method')

    def visit_and(self, matcher: FileMatcherAnd):
        raise NotImplementedError('abstract method')

    def visit_or(self, matcher: FileMatcherOr):
        raise NotImplementedError('abstract method')

    def visit_selectors(self, matcher: FileMatcherFromSelectors):
        raise NotImplementedError('abstract method')
