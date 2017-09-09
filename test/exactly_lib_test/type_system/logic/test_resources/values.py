import pathlib

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_utils.lines_transformer import transformers as sut
from exactly_lib.type_system.logic.file_matcher import FileMatcher
from exactly_lib.type_system.logic.line_matcher import LineMatcher


class FakeLinesTransformer(sut.LinesTransformer):
    def __init__(self):
        pass

    def transform(self, tcds: HomeAndSds, lines: iter) -> iter:
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

    def matches(self, line: str) -> bool:
        raise NotImplementedError('should never be used')
