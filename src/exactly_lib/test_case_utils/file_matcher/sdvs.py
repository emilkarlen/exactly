from typing import Sequence, Callable

from exactly_lib.symbol.logic.file_matcher import FileMatcherSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.matcher.impls import sdv_components, combinator_sdvs
from exactly_lib.test_case_utils.matcher.impls.symbol_reference import MatcherReferenceSdv
from exactly_lib.type_system.logic.file_matcher import FileMatcher, FileMatcherDdv
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable


def file_matcher_constant_sdv(primitive: FileMatcher) -> FileMatcherSdv:
    return FileMatcherSdv(
        sdv_components.matcher_sdv_from_constant_primitive(primitive)
    )


def file_matcher_sdv_from_ddv_parts(references: Sequence[SymbolReference],
                                    make_ddv: Callable[[SymbolTable], FileMatcherDdv]) -> FileMatcherSdv:
    return FileMatcherSdv(
        sdv_components.MatcherSdvFromParts(
            references,
            make_ddv,
        )
    )


def new_reference(name: str) -> FileMatcherSdv:
    return FileMatcherSdv(MatcherReferenceSdv(name, ValueType.FILE_MATCHER))


def new_negation(operand: FileMatcherSdv) -> FileMatcherSdv:
    return FileMatcherSdv(combinator_sdvs.Negation(operand.matcher))


def new_conjunction(operands: Sequence[FileMatcherSdv]) -> FileMatcherSdv:
    return FileMatcherSdv(combinator_sdvs.Conjunction([operand.matcher for operand in operands]))


def new_disjunction(operands: Sequence[FileMatcherSdv]) -> FileMatcherSdv:
    return FileMatcherSdv(combinator_sdvs.Disjunction([operand.matcher for operand in operands]))
