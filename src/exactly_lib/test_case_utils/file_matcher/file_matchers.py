import pathlib
from typing import List, Iterator, Optional

from exactly_lib.definitions import expression
from exactly_lib.test_case_utils.file_matcher.file_matcher_models import FileMatcherModelForPrimitivePath
from exactly_lib.type_system.error_message import ErrorMessageResolver
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


def matching_files_in_dir(matcher: FileMatcher, model: FileMatcherModel) -> Iterator[pathlib.Path]:
    tmp_file_space = model.tmp_file_space
    return (
        path
        for path in model.path.iterdir()
        if matcher.matches(FileMatcherModelForPrimitivePath(tmp_file_space,
                                                            path))
    )
