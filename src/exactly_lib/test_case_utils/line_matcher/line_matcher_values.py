from abc import ABC
from typing import Set, List, Callable

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils.line_matcher.line_matchers import LineMatcherNot, LineMatcherAnd, LineMatcherOr
from exactly_lib.type_system.logic.line_matcher import LineMatcher, LineMatcherValue


class LineMatcherValueFromPrimitiveValue(LineMatcherValue):
    def __init__(self, primitive_value: LineMatcher):
        self._primitive_value = primitive_value

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return set()

    def value_when_no_dir_dependencies(self) -> LineMatcher:
        return self._primitive_value

    def value_of_any_dependency(self, tcds: HomeAndSds) -> LineMatcher:
        return self._primitive_value


class LineMatcherCompositionValueBase(LineMatcherValue, ABC):
    def __init__(self,
                 parts: List[LineMatcherValue],
                 mk_primitive_value: Callable[[List[LineMatcher]], LineMatcher]):
        self._mk_primitive_value = mk_primitive_value
        self._parts = parts
        if not parts:
            raise ValueError('Composition must have at least one element')

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        ret_val = self._parts[0].resolving_dependencies()
        for composed in self._parts[1:]:
            ret_val.update(composed.resolving_dependencies())

        return ret_val

    def value_when_no_dir_dependencies(self) -> LineMatcher:
        return self._mk_primitive_value([
            part.value_when_no_dir_dependencies()
            for part in self._parts
        ])

    def value_of_any_dependency(self, tcds: HomeAndSds) -> LineMatcher:
        return self._mk_primitive_value([
            part.value_of_any_dependency(tcds)
            for part in self._parts
        ])


class LineMatcherNotValue(LineMatcherCompositionValueBase):
    def __init__(self, matcher: LineMatcherValue):
        super().__init__([matcher],
                         lambda values: LineMatcherNot(values[0]))


class LineMatcherAndValue(LineMatcherCompositionValueBase):
    def __init__(self, parts: List[LineMatcherValue]):
        super().__init__(parts,
                         lambda values: LineMatcherAnd(values))


class LineMatcherOrValue(LineMatcherCompositionValueBase):
    def __init__(self, parts: List[LineMatcherValue]):
        super().__init__(parts,
                         lambda values: LineMatcherOr(values))
