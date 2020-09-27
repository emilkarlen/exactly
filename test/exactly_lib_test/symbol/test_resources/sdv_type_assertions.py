from typing import Sequence, Optional, Callable

from exactly_lib.symbol.data.list_sdv import ListSdv
from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.data.string_sdv import StringSdv
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.symbol.sdv_structure import SymbolDependentValue, SymbolReference
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case_utils.files_condition.structure import FilesCondition, FilesConditionSdv, FilesConditionDdv
from exactly_lib.type_system.data.list_ddv import ListDdv
from exactly_lib.type_system.data.path_ddv import PathDdv
from exactly_lib.type_system.data.string_ddv import StringDdv
from exactly_lib.type_system.logic.file_matcher import FileMatcher
from exactly_lib.type_system.logic.files_matcher import FilesMatcher
from exactly_lib.type_system.logic.line_matcher import LineMatcher
from exactly_lib.type_system.logic.matcher_base_class import MatcherDdv, MatcherWTrace
from exactly_lib.type_system.logic.program.program import ProgramDdv, Program
from exactly_lib.type_system.logic.string_matcher import StringMatcher
from exactly_lib.type_system.logic.string_transformer import StringTransformer, StringTransformerDdv
from exactly_lib.util.symbol_table import SymbolTable, symbol_table_from_none_or_value
from exactly_lib_test.symbol.test_resources.sdv_assertions import matches_sdv
from exactly_lib_test.tcfs.test_resources.paths import fake_tcds
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.logic.test_resources import logic_structure_assertions as asrt_logic


def matches_matcher_sdv(primitive_value: ValueAssertion[MatcherWTrace] = asrt.anything_goes(),
                        references: ValueAssertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
                        symbols: SymbolTable = None,
                        tcds: TestCaseDs = fake_tcds(),
                        ) -> ValueAssertion[SymbolDependentValue]:
    return matches_sdv(
        asrt.is_instance(MatcherSdv),
        references,
        asrt.is_instance_with(
            MatcherDdv,
            asrt_logic.matches_matcher_ddv(
                lambda tcds_: primitive_value,
                tcds
            )
        ),
        asrt.anything_goes(),
        symbol_table_from_none_or_value(symbols)
    )


def matches_sdv_of_string(references: ValueAssertion[Sequence[SymbolReference]],
                          ddv: ValueAssertion[StringDdv],
                          custom: ValueAssertion[StringSdv] = asrt.anything_goes(),
                          symbols: Optional[SymbolTable] = None) -> ValueAssertion[SymbolDependentValue]:
    return matches_sdv(asrt.is_instance(StringSdv),
                       references,
                       asrt.is_instance_with(StringDdv, ddv),
                       custom,
                       symbol_table_from_none_or_value(symbols))


def matches_sdv_of_list(references: ValueAssertion[Sequence[SymbolReference]],
                        ddv: ValueAssertion[ListDdv],
                        custom: ValueAssertion[ListSdv] = asrt.anything_goes(),
                        symbols: Optional[SymbolTable] = None) -> ValueAssertion[SymbolDependentValue]:
    return matches_sdv(asrt.is_instance(ListSdv),
                       references,
                       asrt.is_instance_with(ListDdv, ddv),
                       custom,
                       symbol_table_from_none_or_value(symbols))


def matches_sdv_of_path(references: ValueAssertion[Sequence[SymbolReference]],
                        ddv: ValueAssertion[PathDdv],
                        custom: ValueAssertion[PathSdv] = asrt.anything_goes(),
                        symbols: Optional[SymbolTable] = None) -> ValueAssertion[SymbolDependentValue]:
    return matches_sdv(asrt.is_instance(PathSdv),
                       references,
                       asrt.is_instance_with(PathDdv, ddv),
                       custom,
                       symbol_table_from_none_or_value(symbols))


def matches_sdv_of_file_matcher(references: ValueAssertion[Sequence[SymbolReference]] = asrt.anything_goes(),
                                primitive_value: ValueAssertion[FileMatcher] = asrt.anything_goes(),
                                symbols: Optional[SymbolTable] = None,
                                tcds: TestCaseDs = fake_tcds(),
                                ) -> ValueAssertion[SymbolDependentValue]:
    return matches_matcher_sdv(
        primitive_value,
        references,
        symbols,
        tcds)


def matches_sdv_of_files_matcher(references: ValueAssertion[Sequence[SymbolReference]] = asrt.anything_goes(),
                                 primitive_value: ValueAssertion[FilesMatcher] = asrt.anything_goes(),
                                 symbols: Optional[SymbolTable] = None,
                                 tcds: TestCaseDs = fake_tcds(),
                                 ) -> ValueAssertion[SymbolDependentValue]:
    return matches_matcher_sdv(
        primitive_value,
        references,
        symbols,
        tcds)


def matches_sdv_of_line_matcher(references: ValueAssertion[Sequence[SymbolReference]] = asrt.anything_goes(),
                                primitive_value: ValueAssertion[LineMatcher] = asrt.anything_goes(),
                                symbols: Optional[SymbolTable] = None,
                                tcds: TestCaseDs = fake_tcds(),
                                ) -> ValueAssertion[SymbolDependentValue]:
    return matches_matcher_sdv(
        primitive_value,
        references,
        symbols,
        tcds)


def matches_sdv_of_string_matcher(references: ValueAssertion[Sequence[SymbolReference]] = asrt.anything_goes(),
                                  primitive_value: ValueAssertion[StringMatcher] = asrt.anything_goes(),
                                  symbols: Optional[SymbolTable] = None,
                                  tcds: TestCaseDs = fake_tcds(),
                                  ) -> ValueAssertion[SymbolDependentValue]:
    return matches_matcher_sdv(
        primitive_value,
        references,
        symbols,
        tcds)


def matches_sdv_of_files_condition_constant(
        references: ValueAssertion[Sequence[SymbolReference]] = asrt.anything_goes(),
        primitive_value: ValueAssertion[FilesCondition] = asrt.anything_goes(),
        symbols: SymbolTable = None
) -> ValueAssertion[SymbolDependentValue]:
    return matches_sdv(
        asrt.is_instance(FilesConditionSdv),
        references,
        asrt.is_instance_with(
            FilesConditionDdv,
            asrt_logic.matches_logic_ddv(
                lambda tcds: asrt.is_instance_with(FilesCondition, primitive_value)
            )
        ),
        asrt.anything_goes(),
        symbol_table_from_none_or_value(symbols)
    )


def matches_sdv_of_string_transformer_constant(
        references: ValueAssertion[Sequence[SymbolReference]] = asrt.anything_goes(),
        primitive_value: ValueAssertion[StringTransformer] = asrt.anything_goes(),
        symbols: SymbolTable = None
) -> ValueAssertion[SymbolDependentValue]:
    return matches_sdv(
        asrt.is_instance(StringTransformerSdv),
        references,
        asrt.is_instance_with(
            StringTransformerDdv,
            asrt_logic.matches_logic_ddv(
                lambda tcds: asrt.is_instance_with(StringTransformer, primitive_value)
            )
        ),
        asrt.anything_goes(),
        symbol_table_from_none_or_value(symbols)
    )


def matches_sdv_of_program(references: ValueAssertion[Sequence[SymbolReference]],
                           primitive_value: Callable[[TestCaseDs], ValueAssertion[Program]],
                           symbols: Optional[SymbolTable] = None
                           ) -> ValueAssertion[SymbolDependentValue]:
    return matches_sdv(
        asrt.is_instance(ProgramSdv),
        references,
        asrt.is_instance_with(
            ProgramDdv,
            asrt_logic.matches_logic_ddv(
                lambda tcds: asrt.is_instance_with(Program, primitive_value(tcds))
            )
        ),
        asrt.anything_goes(),
        symbol_table_from_none_or_value(symbols)
    )


def matches_sdv_of_program_constant(references: ValueAssertion[Sequence[SymbolReference]],
                                    primitive_value: ValueAssertion[Program],
                                    symbols: Optional[SymbolTable] = None
                                    ) -> ValueAssertion[SymbolDependentValue]:
    return matches_sdv_of_program(
        references,
        lambda tcds: primitive_value,
        symbols
    )
