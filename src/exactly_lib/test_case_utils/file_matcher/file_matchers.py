import pathlib
from typing import List, Iterator, Pattern, Optional

from exactly_lib.definitions import expression
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.file_matcher.file_matcher_models import FileMatcherModelForPrimitivePath
from exactly_lib.type_system.error_message import ErrorMessageResolver, ConstantErrorMessageResolver
from exactly_lib.type_system.logic.file_matcher import FileMatcher, FileMatcherModel


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

    def matches(self, model: FileMatcherModel) -> bool:
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

    def matches2(self, model: FileMatcherModel) -> Optional[ErrorMessageResolver]:
        if self.matches(model):
            return None
        else:
            return ConstantErrorMessageResolver(str(model.path))

    def matches(self, model: FileMatcherModel) -> bool:
        return model.path.match(self._glob_pattern)


class FileMatcherBaseNameRegExPattern(FileMatcher):
    """Matches the base name of a path on a regular expression."""

    def __init__(self, compiled_reg_ex: Pattern):
        self._compiled_reg_ex = compiled_reg_ex

    @property
    def reg_ex_pattern(self) -> str:
        return self._compiled_reg_ex.pattern

    @property
    def option_description(self) -> str:
        return 'base name matches regular expression ' + self.reg_ex_pattern

    def matches2(self, model: FileMatcherModel) -> Optional[ErrorMessageResolver]:
        if self.matches(model):
            return None
        else:
            return ConstantErrorMessageResolver(str(model.path.name))

    def matches(self, model: FileMatcherModel) -> bool:
        return self._compiled_reg_ex.search(model.path.name) is not None


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

    def matches(self, model: FileMatcherModel) -> bool:
        return self._pathlib_predicate(model.path)


class FileMatcherNot(FileMatcher):
    """Matcher that negates a given matcher."""

    def __init__(self, matcher: FileMatcher):
        self._matcher = matcher

    @property
    def negated_matcher(self) -> FileMatcher:
        return self._matcher

    @property
    def option_description(self) -> str:
        return expression.NOT_OPERATOR_NAME + ' ' + self._matcher.option_description

    def matches(self, model: FileMatcherModel) -> bool:
        return not self._matcher.matches(model)


class FileMatcherAnd(FileMatcher):
    """Matcher that and:s a list of matchers."""

    def __init__(self, matchers: List[FileMatcher]):
        self._matchers = tuple(matchers)

    @property
    def matchers(self) -> List[FileMatcher]:
        return list(self._matchers)

    @property
    def option_description(self) -> str:
        op = ' ' + expression.AND_OPERATOR_NAME + ' '
        return '({})'.format(op.join(map(lambda fm: fm.option_description, self.matchers)))

    def matches2(self, model: FileMatcherModel) -> Optional[ErrorMessageResolver]:
        for matcher in self._matchers:
            error = matcher.matches2(model)
            if error is not None:
                return error
        return None

    def matches(self, model: FileMatcherModel) -> bool:
        return all((matcher.matches(model)
                    for matcher in self._matchers))


class FileMatcherOr(FileMatcher):
    """Matcher that or:s a list of matchers."""

    def __init__(self, matchers: List[FileMatcher]):
        self._matchers = tuple(matchers)

    @property
    def option_description(self) -> str:
        op = ' ' + expression.OR_OPERATOR_NAME + ' '
        return '({})'.format(op.join(map(lambda fm: fm.option_description, self.matchers)))

    @property
    def matchers(self) -> List[FileMatcher]:
        return list(self._matchers)

    def matches(self, model: FileMatcherModel) -> bool:
        return any((matcher.matches(model)
                    for matcher in self._matchers))


MATCH_EVERY_FILE = FileMatcherConstant(True)


class FileMatcherStructureVisitor:
    """
    Visits all variants of :class:`FileMatcher`.

    The existence of this class means that the structure of :class:`FileMatcher`s
    is fixed. The reason for this is to, among other things, support optimizations
    of selectors.

    REFACT 2019-04-26: This class should be removed - there should be
    no need for a fixed hierarchy of FileMatcher.s.
    """

    def visit(self, matcher: FileMatcher):
        if isinstance(matcher, FileMatcherNameGlobPattern):
            return self.visit_name_glob_pattern(matcher)
        if isinstance(matcher, FileMatcherBaseNameRegExPattern):
            return self.visit_name_reg_ex_pattern(matcher)
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

    def visit_name_reg_ex_pattern(self, matcher: FileMatcherBaseNameRegExPattern):
        raise NotImplementedError('abstract method')

    def visit_type(self, matcher: FileMatcherType):
        raise NotImplementedError('abstract method')

    def visit_not(self, matcher: FileMatcherNot):
        raise NotImplementedError('abstract method')

    def visit_and(self, matcher: FileMatcherAnd):
        raise NotImplementedError('abstract method')

    def visit_or(self, matcher: FileMatcherOr):
        raise NotImplementedError('abstract method')


def matching_files_in_dir(matcher: FileMatcher, model: FileMatcherModel) -> Iterator[pathlib.Path]:
    tmp_file_space = model.tmp_file_space
    return (
        path
        for path in model.path.iterdir()
        if matcher.matches(FileMatcherModelForPrimitivePath(tmp_file_space,
                                                            path))
    )
