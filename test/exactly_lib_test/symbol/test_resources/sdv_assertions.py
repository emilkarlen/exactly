import unittest
from typing import Sequence, Optional

from exactly_lib.symbol.data.list_sdv import ListSdv
from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.data.string_sdv import StringSdv
from exactly_lib.symbol.logic.logic_type_sdv import LogicSdv
from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.symbol.sdv_structure import SymbolReference, SymbolDependentValue
from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependentValue
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.data.list_ddv import ListDdv
from exactly_lib.type_system.data.path_ddv import PathDdv
from exactly_lib.type_system.data.string_ddv import StringDdv
from exactly_lib.type_system.logic.file_matcher import FileMatcher
from exactly_lib.type_system.logic.files_matcher import FilesMatcher
from exactly_lib.type_system.logic.line_matcher import LineMatcher
from exactly_lib.type_system.logic.program.program import ProgramDdv
from exactly_lib.type_system.logic.string_matcher import StringMatcher
from exactly_lib.type_system.logic.string_transformer import StringTransformer
from exactly_lib.util.file_utils import TmpDirFileSpace, TmpDirFileSpaceThatMustNoBeUsed
from exactly_lib.util.symbol_table import SymbolTable, symbol_table_from_none_or_value
from exactly_lib_test.symbol.test_resources.sdv_structure_assertions import is_sdv_of_logic_type
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_tcds
from exactly_lib_test.test_case_utils.matcher.test_resources.assertions import matches_matcher_sdv
from exactly_lib_test.test_case_utils.test_resources import sdv_assertions
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase


def matches_sdv(sdv_type: ValueAssertion[SymbolDependentValue],
                references: ValueAssertion[Sequence[SymbolReference]],
                resolved_value: ValueAssertion[DirDependentValue],
                custom: ValueAssertion[SymbolDependentValue] = asrt.anything_goes(),
                symbols: Optional[SymbolTable] = None) -> ValueAssertion[SymbolDependentValue]:
    return _MatchesSdv(sdv_type,
                       references,
                       resolved_value,
                       custom,
                       symbol_table_from_none_or_value(symbols))


def is_sdv_of_string_type() -> ValueAssertion[SymbolDependentValue]:
    return asrt.is_instance(StringSdv)


def is_sdv_of_path_type() -> ValueAssertion[SymbolDependentValue]:
    return asrt.is_instance(PathSdv)


def is_sdv_of_list_type() -> ValueAssertion[SymbolDependentValue]:
    return asrt.is_instance(ListSdv)


def is_sdv_of_program_type() -> ValueAssertion[SymbolDependentValue]:
    return is_sdv_of_logic_type(ProgramSdv)


def matches_sdv_of_string(references: ValueAssertion[Sequence[SymbolReference]],
                          resolved_value: ValueAssertion[StringDdv],
                          custom: ValueAssertion[StringSdv] = asrt.anything_goes(),
                          symbols: Optional[SymbolTable] = None) -> ValueAssertion[SymbolDependentValue]:
    return matches_sdv(is_sdv_of_string_type(),
                       references,
                       asrt.is_instance_with(StringDdv, resolved_value),
                       custom,
                       symbol_table_from_none_or_value(symbols))


def matches_sdv_of_list(references: ValueAssertion[Sequence[SymbolReference]],
                        resolved_value: ValueAssertion[ListDdv],
                        custom: ValueAssertion[ListSdv] = asrt.anything_goes(),
                        symbols: Optional[SymbolTable] = None) -> ValueAssertion[SymbolDependentValue]:
    return matches_sdv(is_sdv_of_list_type(),
                       references,
                       asrt.is_instance_with(ListDdv, resolved_value),
                       custom,
                       symbol_table_from_none_or_value(symbols))


def matches_sdv_of_path(references: ValueAssertion[Sequence[SymbolReference]],
                        resolved_value: ValueAssertion[PathDdv],
                        custom: ValueAssertion[PathSdv] = asrt.anything_goes(),
                        symbols: Optional[SymbolTable] = None) -> ValueAssertion[SymbolDependentValue]:
    return matches_sdv(is_sdv_of_path_type(),
                       references,
                       asrt.is_instance_with(PathDdv, resolved_value),
                       custom,
                       symbol_table_from_none_or_value(symbols))


def matches_sdv_of_file_matcher(references: ValueAssertion[Sequence[SymbolReference]] = asrt.anything_goes(),
                                primitive_value: ValueAssertion[FileMatcher] = asrt.anything_goes(),
                                symbols: Optional[SymbolTable] = None,
                                tcds: Tcds = fake_tcds(),
                                tmp_file_space: TmpDirFileSpace = TmpDirFileSpaceThatMustNoBeUsed(),
                                ) -> ValueAssertion[SymbolDependentValue]:
    return matches_matcher_sdv(
        primitive_value,
        references,
        symbol_table_from_none_or_value(symbols),
        tcds,
        tmp_file_space,
    )


def matches_sdv_of_files_matcher(references: ValueAssertion[Sequence[SymbolReference]] = asrt.anything_goes(),
                                 primitive_value: ValueAssertion[FilesMatcher] = asrt.anything_goes(),
                                 symbols: Optional[SymbolTable] = None,
                                 tcds: Tcds = fake_tcds(),
                                 tmp_file_space: TmpDirFileSpace = TmpDirFileSpaceThatMustNoBeUsed(),
                                 ) -> ValueAssertion[SymbolDependentValue]:
    return matches_matcher_sdv(
        primitive_value,
        references,
        symbol_table_from_none_or_value(symbols),
        tcds,
        tmp_file_space,
    )


def matches_sdv_of_line_matcher(references: ValueAssertion[Sequence[SymbolReference]] = asrt.anything_goes(),
                                primitive_value: ValueAssertion[LineMatcher] = asrt.anything_goes(),
                                symbols: Optional[SymbolTable] = None,
                                tcds: Tcds = fake_tcds(),
                                tmp_file_space: TmpDirFileSpace = TmpDirFileSpaceThatMustNoBeUsed(),
                                ) -> ValueAssertion[SymbolDependentValue]:
    return matches_matcher_sdv(
        primitive_value,
        references,
        symbol_table_from_none_or_value(symbols),
        tcds,
        tmp_file_space,
    )


def matches_sdv_of_string_matcher(references: ValueAssertion[Sequence[SymbolReference]] = asrt.anything_goes(),
                                  primitive_value: ValueAssertion[StringMatcher] = asrt.anything_goes(),
                                  symbols: Optional[SymbolTable] = None,
                                  tcds: Tcds = fake_tcds(),
                                  tmp_file_space: TmpDirFileSpace = TmpDirFileSpaceThatMustNoBeUsed(),
                                  ) -> ValueAssertion[SymbolDependentValue]:
    return matches_matcher_sdv(
        primitive_value,
        references,
        symbol_table_from_none_or_value(symbols),
        tcds,
        tmp_file_space,
    )


def matches_sdv_of_string_transformer(
        primitive_value: ValueAssertion[StringTransformer],
        references: ValueAssertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
        symbols: SymbolTable = None
) -> ValueAssertion[LogicSdv]:
    return sdv_assertions.matches_sdv_of_logic_type__w_adv(StringTransformerSdv,
                                                           asrt.is_instance_with(StringTransformer,
                                                                                 primitive_value),
                                                           references,
                                                           symbols)


def matches_sdv_of_program(references: ValueAssertion[Sequence[SymbolReference]],
                           resolved_program_value: ValueAssertion[DirDependentValue],
                           custom: ValueAssertion[ProgramSdv] = asrt.anything_goes(),
                           symbols: Optional[SymbolTable] = None) -> ValueAssertion[SymbolDependentValue]:
    return matches_sdv(is_sdv_of_program_type(),
                       references,
                       asrt.is_instance_with(ProgramDdv, resolved_program_value),
                       custom,
                       symbol_table_from_none_or_value(symbols))


class _MatchesSdv(ValueAssertionBase[SymbolDependentValue]):
    """Implements as class to make it possible to set break points"""

    def __init__(self,
                 sdv_type: ValueAssertion[SymbolDependentValue],
                 references: ValueAssertion[Sequence[SymbolReference]],
                 resolved_value: ValueAssertion[DirDependentValue],
                 custom: ValueAssertion[SymbolDependentValue],
                 symbols: SymbolTable):
        self.sdv_type = sdv_type
        self.references = references
        self.resolved_value = resolved_value
        self.custom = custom
        self.symbols = symbols

    def _apply(self,
               put: unittest.TestCase,
               value: SymbolDependentValue,
               message_builder: asrt.MessageBuilder):
        put.assertIsInstance(value, SymbolDependentValue,
                             message_builder.apply("SDV type"))

        self.sdv_type.apply(put, value, message_builder)

        self.references.apply(put, value.references,
                              message_builder.for_sub_component('references'))

        self.custom.apply(put, value, message_builder)

        resolved_value = value.resolve(self.symbols)

        self.resolved_value.apply(put, resolved_value,
                                  message_builder.for_sub_component('resolved value'))
