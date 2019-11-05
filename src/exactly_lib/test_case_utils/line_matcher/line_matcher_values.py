from typing import Set, Callable, Optional, Sequence

from exactly_lib.test_case.validation import pre_or_post_value_validation, pre_or_post_value_validators
from exactly_lib.test_case.validation.pre_or_post_value_validation import PreOrPostSdsValueValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils.line_matcher import line_matchers
from exactly_lib.type_system.description.tree_structured import StructureRenderer, WithTreeStructureDescription
from exactly_lib.type_system.logic.impls import combinator_matchers
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

    def structure(self) -> StructureRenderer:
        return self._primitive_value.structure()

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self._resolving_dependencies

    @property
    def validator(self) -> PreOrPostSdsValueValidator:
        return self._validator

    def value_when_no_dir_dependencies(self) -> LineMatcher:
        return self._primitive_value

    def value_of_any_dependency(self, tcds: HomeAndSds) -> LineMatcher:
        return self._primitive_value


class _LineMatcherCompositionValueBase(LineMatcherValue):
    def __init__(self,
                 parts: Sequence[LineMatcherValue],
                 mk_primitive_value: Callable[[Sequence[LineMatcher]], LineMatcher],
                 mk_structure: Callable[[Sequence[WithTreeStructureDescription]], StructureRenderer]):
        self._mk_primitive_value = mk_primitive_value
        self._mk_structure = mk_structure
        self._parts = parts
        if not parts:
            raise ValueError('Composition must have at least one element')
        self._validator = pre_or_post_value_validators.all_of([
            part.validator
            for part in parts
        ])

    def structure(self) -> StructureRenderer:
        return self._mk_structure(self._parts)

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        ret_val = self._parts[0].resolving_dependencies()
        for composed in self._parts[1:]:
            ret_val.update(composed.resolving_dependencies())

        return ret_val

    @property
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


def negation(matcher: LineMatcherValue) -> LineMatcherValue:
    return _LineMatcherCompositionValueBase(
        [matcher],
        lambda values: line_matchers.negation(values[0]),
        lambda values: combinator_matchers.Negation.new_structure_tree(values[0]),
    )


def conjunction(parts: Sequence[LineMatcherValue]) -> LineMatcherValue:
    return _LineMatcherCompositionValueBase(
        parts,
        line_matchers.conjunction,
        combinator_matchers.Conjunction.new_structure_tree,
    )


def disjunction(parts: Sequence[LineMatcherValue]) -> LineMatcherValue:
    return _LineMatcherCompositionValueBase(
        parts,
        line_matchers.disjunction,
        combinator_matchers.Disjunction.new_structure_tree,
    )
