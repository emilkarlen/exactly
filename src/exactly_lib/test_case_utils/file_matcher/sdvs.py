from typing import Sequence

from exactly_lib.test_case_utils.matcher.impls import sdv_components, combinator_sdvs
from exactly_lib.test_case_utils.matcher.impls.symbol_reference import MatcherReferenceSdv
from exactly_lib.type_system.logic.file_matcher import FileMatcher, FileMatcherSdv
from exactly_lib.type_system.value_type import ValueType


def file_matcher_constant_sdv(primitive: FileMatcher) -> FileMatcherSdv:
    return sdv_components.matcher_sdv_from_constant_primitive(primitive)


def new_reference(name: str) -> FileMatcherSdv:
    return MatcherReferenceSdv(name, ValueType.FILE_MATCHER)


def new_negation(operand: FileMatcherSdv) -> FileMatcherSdv:
    return combinator_sdvs.Negation(operand)


def new_conjunction(operands: Sequence[FileMatcherSdv]) -> FileMatcherSdv:
    return combinator_sdvs.Conjunction(operands)


def new_disjunction(operands: Sequence[FileMatcherSdv]) -> FileMatcherSdv:
    return combinator_sdvs.Disjunction(operands)
