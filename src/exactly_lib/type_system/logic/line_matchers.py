from typing import Set, Iterator, Tuple

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.type_system.logic.line_matcher import LineMatcher, LineMatcherValue, LineMatcherLine


class LineMatcherValueFromPrimitiveValue(LineMatcherValue):
    def __init__(self, primitive_value: LineMatcher):
        self._primitive_value = primitive_value

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return set()

    def value_when_no_dir_dependencies(self) -> LineMatcher:
        return self._primitive_value

    def value_of_any_dependency(self, tcds: HomeAndSds) -> LineMatcher:
        return self._primitive_value


def model_iter_from_file_line_iter(lines: Iterator[str]) -> Iterator[LineMatcherLine]:
    """
    Gives a sequence of line matcher models, corresponding to input lines read from file.
    New lines are expected to appear only as last character of lines, or not at all, if
    last line is not ended with new line in the file.

    @:param strings: lines from an input source
    """
    return enumerate((l.rstrip('\n') for l in lines),
                     1)


def original_and_model_iter_from_file_line_iter(lines: Iterator[str]) -> Iterator[Tuple[str, LineMatcherLine]]:
    """
    Gives a sequence of pairs, corresponding to each element in lines.
    (original line, line-matcher-model-for-line).

    See also docs of model_iter_from_file_line_iter.

    @:param strings: lines from an input source
    """
    return (
        (original, (line_num, original.rstrip('\n')))
        for line_num, original in enumerate(lines, 1)
    )
