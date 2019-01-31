from abc import ABC
from typing import Set, List, Callable, Optional

from exactly_lib.test_case import pre_or_post_value_validation
from exactly_lib.test_case import pre_or_post_value_validators
from exactly_lib.test_case.pre_or_post_value_validation import PreOrPostSdsValueValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils.line_matcher.line_matchers import LineMatcherNot, LineMatcherAnd, LineMatcherOr
from exactly_lib.type_system.logic.line_matcher import LineMatcher, LineMatcherValue


class LineMatcherValueFromPrimitiveValue(LineMatcherValue):
    def __init__(self,
                 primitive_value: LineMatcher,
                 validator: PreOrPostSdsValueValidator =
                 pre_or_post_value_validation.constant_success_validator(),
                 resolving_dependencies: Optional[Set[DirectoryStructurePartition]] = None):
        self._primitive_value = primitive_value
        self._validator = validator
        self._resolving_dependencies = (set()
                                        if resolving_dependencies is None
                                        else resolving_dependencies)

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self._resolving_dependencies

    def validator(self) -> PreOrPostSdsValueValidator:
        return self._validator

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
        self._validator = pre_or_post_value_validators.all_of([
            part.validator()
            for part in parts
        ])

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        ret_val = self._parts[0].resolving_dependencies()
        for composed in self._parts[1:]:
            ret_val.update(composed.resolving_dependencies())

        return ret_val

    def validator(self) -> PreOrPostSdsValueValidator:
        return self._validator

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
