import pathlib
from typing import Iterable, Callable

from exactly_lib.test_case_utils.string_transformer import transformers as sut
from exactly_lib.type_system.logic.file_matcher import FileMatcher
from exactly_lib.type_system.logic.line_matcher import LineMatcher, LineMatcherLine


class FakeStringTransformer(sut.StringTransformer):
    def __init__(self):
        pass

    def transform(self, lines: Iterable[str]) -> Iterable[str]:
        raise NotImplementedError('should never be used')


class FileMatcherTestImpl(FileMatcher):
    @property
    def option_description(self) -> str:
        return str(type(self))

    def matches(self, path: pathlib.Path) -> bool:
        raise NotImplementedError('should never be used')


class LineMatcherNotImplementedTestImpl(LineMatcher):
    @property
    def option_description(self) -> str:
        return str(type(self))

    def matches(self, line: LineMatcherLine) -> bool:
        raise NotImplementedError('should never be used')


def is_identical_to(line_num: int, line_contents: str) -> LineMatcher:
    return LineMatcherFromPredicates(lambda x: x == line_num,
                                     lambda x: x == line_contents)


class LineMatcherFromPredicates(LineMatcher):
    def __init__(self,
                 line_num_predicate: Callable[[int], bool] = lambda x: True,
                 line_contents_predicate: Callable[[str], bool] = lambda x: True):
        self.line_num = line_num_predicate
        self.line_contents = line_contents_predicate

    def matches(self, line: LineMatcherLine) -> bool:
        return self.line_num(line[0]) and \
               self.line_contents(line[1])

    @property
    def option_description(self) -> str:
        return str(type(self))
