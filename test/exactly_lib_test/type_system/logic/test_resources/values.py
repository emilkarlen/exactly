from typing import Iterable, Callable

from exactly_lib.test_case_utils.file_matcher.impl.impl_base_class import FileMatcherImplBase
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel
from exactly_lib.type_system.logic.line_matcher import LineMatcher, LineMatcherLine
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.type_system.logic.string_transformer import StringTransformer


class FakeStringTransformer(StringTransformer):
    def __init__(self):
        pass

    def transform(self, lines: Iterable[str]) -> Iterable[str]:
        raise NotImplementedError('should never be used')


class FileMatcherTestImpl(FileMatcherImplBase):
    @property
    def name(self) -> str:
        return str(type(self))

    @property
    def option_description(self) -> str:
        return str(type(self))

    def matches(self, model: FileMatcherModel) -> bool:
        raise NotImplementedError('should never be used')

    def matches_w_trace(self, model: FileMatcherModel) -> MatchingResult:
        raise NotImplementedError('should never be used')


class LineMatcherNotImplementedTestImpl(LineMatcher):
    @property
    def name(self) -> str:
        return str(type(self))

    @property
    def option_description(self) -> str:
        return str(type(self))

    def matches_w_trace(self, line: LineMatcherLine) -> MatchingResult:
        raise NotImplementedError('should never be used')

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

    @property
    def name(self) -> str:
        return str(type(self))

    @property
    def option_description(self) -> str:
        return str(type(self))

    def matches_w_trace(self, line: LineMatcherLine) -> MatchingResult:
        return self._new_tb().build_result(self.matches(line))

    def matches(self, line: LineMatcherLine) -> bool:
        return self.line_num(line[0]) and \
               self.line_contents(line[1])
