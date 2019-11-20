from typing import Callable, Sequence

from exactly_lib.test_case.validation import pre_or_post_value_validation, pre_or_post_value_validators
from exactly_lib.test_case.validation.pre_or_post_value_validation import PreOrPostSdsValueValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.line_matcher import line_matchers
from exactly_lib.type_system.description.tree_structured import StructureRenderer, WithTreeStructureDescription
from exactly_lib.type_system.logic.impls import combinator_matchers
from exactly_lib.type_system.logic.line_matcher import LineMatcher, LineMatcherDdv


class LineMatcherValueFromPrimitiveDdv(LineMatcherDdv):
    def __init__(self,
                 primitive_value: LineMatcher,
                 validator: PreOrPostSdsValueValidator =
                 pre_or_post_value_validation.constant_success_validator()):
        self._primitive_value = primitive_value
        self._validator = validator

    def structure(self) -> StructureRenderer:
        return self._primitive_value.structure()

    @property
    def validator(self) -> PreOrPostSdsValueValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: Tcds) -> LineMatcher:
        return self._primitive_value


class _LineMatcherCompositionDdvBase(LineMatcherDdv):
    def __init__(self,
                 parts: Sequence[LineMatcherDdv],
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

    @property
    def validator(self) -> PreOrPostSdsValueValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: Tcds) -> LineMatcher:
        return self._mk_primitive_value([
            part.value_of_any_dependency(tcds)
            for part in self._parts
        ])


def negation(operand: LineMatcherDdv) -> LineMatcherDdv:
    return _LineMatcherCompositionDdvBase(
        [operand],
        lambda values: line_matchers.negation(values[0]),
        lambda values: combinator_matchers.Negation.new_structure_tree(values[0]),
    )


def conjunction(operands: Sequence[LineMatcherDdv]) -> LineMatcherDdv:
    return _LineMatcherCompositionDdvBase(
        operands,
        line_matchers.conjunction,
        combinator_matchers.Conjunction.new_structure_tree,
    )


def disjunction(operands: Sequence[LineMatcherDdv]) -> LineMatcherDdv:
    return _LineMatcherCompositionDdvBase(
        operands,
        line_matchers.disjunction,
        combinator_matchers.Disjunction.new_structure_tree,
    )
