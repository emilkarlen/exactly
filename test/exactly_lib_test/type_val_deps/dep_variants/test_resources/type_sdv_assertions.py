from typing import Sequence, Optional, Callable

from exactly_lib.symbol.sdv_structure import SymbolDependentValue, SymbolReference
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.ddv.matcher import MatcherDdv
from exactly_lib.type_val_deps.types.files_condition.sdv import FilesCondition, FilesConditionSdv, FilesConditionDdv
from exactly_lib.type_val_deps.types.list_.list_ddv import ListDdv
from exactly_lib.type_val_deps.types.list_.list_sdv import ListSdv
from exactly_lib.type_val_deps.types.matcher import MatcherSdv
from exactly_lib.type_val_deps.types.path.path_ddv import PathDdv
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv
from exactly_lib.type_val_deps.types.program.ddv.program import ProgramDdv
from exactly_lib.type_val_deps.types.program.sdv.program import ProgramSdv
from exactly_lib.type_val_deps.types.string_.string_ddv import StringDdv
from exactly_lib.type_val_deps.types.string_.string_sdv import StringSdv
from exactly_lib.type_val_deps.types.string_transformer.ddv import StringTransformerDdv
from exactly_lib.type_val_deps.types.string_transformer.sdv import StringTransformerSdv
from exactly_lib.type_val_prims.matcher.file_matcher import FileMatcher
from exactly_lib.type_val_prims.matcher.files_matcher import FilesMatcher
from exactly_lib.type_val_prims.matcher.line_matcher import LineMatcher
from exactly_lib.type_val_prims.matcher.matcher_base_class import MatcherWTrace
from exactly_lib.type_val_prims.matcher.string_matcher import StringMatcher
from exactly_lib.type_val_prims.program.program import Program
from exactly_lib.type_val_prims.string_transformer import StringTransformer
from exactly_lib.util.symbol_table import SymbolTable, symbol_table_from_none_or_value
from exactly_lib_test.tcfs.test_resources.fake_ds import fake_tcds
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.dep_variants.test_resources import logic_structure_assertions as asrt_logic
from exactly_lib_test.type_val_deps.sym_ref.test_resources.sdv_assertions import matches_sdv


def matches_matcher_sdv(primitive_value: Assertion[MatcherWTrace] = asrt.anything_goes(),
                        references: Assertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
                        symbols: SymbolTable = None,
                        tcds: TestCaseDs = fake_tcds(),
                        ) -> Assertion[SymbolDependentValue]:
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


def matches_sdv_of_string(references: Assertion[Sequence[SymbolReference]],
                          ddv: Assertion[StringDdv],
                          custom: Assertion[StringSdv] = asrt.anything_goes(),
                          symbols: Optional[SymbolTable] = None) -> Assertion[SymbolDependentValue]:
    return matches_sdv(asrt.is_instance(StringSdv),
                       references,
                       asrt.is_instance_with(StringDdv, ddv),
                       custom,
                       symbol_table_from_none_or_value(symbols))


def matches_sdv_of_list(references: Assertion[Sequence[SymbolReference]],
                        ddv: Assertion[ListDdv],
                        custom: Assertion[ListSdv] = asrt.anything_goes(),
                        symbols: Optional[SymbolTable] = None) -> Assertion[SymbolDependentValue]:
    return matches_sdv(asrt.is_instance(ListSdv),
                       references,
                       asrt.is_instance_with(ListDdv, ddv),
                       custom,
                       symbol_table_from_none_or_value(symbols))


def matches_sdv_of_path(references: Assertion[Sequence[SymbolReference]],
                        ddv: Assertion[PathDdv],
                        custom: Assertion[PathSdv] = asrt.anything_goes(),
                        symbols: Optional[SymbolTable] = None) -> Assertion[SymbolDependentValue]:
    return matches_sdv(asrt.is_instance(PathSdv),
                       references,
                       asrt.is_instance_with(PathDdv, ddv),
                       custom,
                       symbol_table_from_none_or_value(symbols))


def matches_sdv_of_file_matcher(references: Assertion[Sequence[SymbolReference]] = asrt.anything_goes(),
                                primitive_value: Assertion[FileMatcher] = asrt.anything_goes(),
                                symbols: Optional[SymbolTable] = None,
                                tcds: TestCaseDs = fake_tcds(),
                                ) -> Assertion[SymbolDependentValue]:
    return matches_matcher_sdv(
        primitive_value,
        references,
        symbols,
        tcds)


def matches_sdv_of_files_matcher(references: Assertion[Sequence[SymbolReference]] = asrt.anything_goes(),
                                 primitive_value: Assertion[FilesMatcher] = asrt.anything_goes(),
                                 symbols: Optional[SymbolTable] = None,
                                 tcds: TestCaseDs = fake_tcds(),
                                 ) -> Assertion[SymbolDependentValue]:
    return matches_matcher_sdv(
        primitive_value,
        references,
        symbols,
        tcds)


def matches_sdv_of_line_matcher(references: Assertion[Sequence[SymbolReference]] = asrt.anything_goes(),
                                primitive_value: Assertion[LineMatcher] = asrt.anything_goes(),
                                symbols: Optional[SymbolTable] = None,
                                tcds: TestCaseDs = fake_tcds(),
                                ) -> Assertion[SymbolDependentValue]:
    return matches_matcher_sdv(
        primitive_value,
        references,
        symbols,
        tcds)


def matches_sdv_of_string_matcher(references: Assertion[Sequence[SymbolReference]] = asrt.anything_goes(),
                                  primitive_value: Assertion[StringMatcher] = asrt.anything_goes(),
                                  symbols: Optional[SymbolTable] = None,
                                  tcds: TestCaseDs = fake_tcds(),
                                  ) -> Assertion[SymbolDependentValue]:
    return matches_matcher_sdv(
        primitive_value,
        references,
        symbols,
        tcds)


def matches_sdv_of_files_condition_constant(
        references: Assertion[Sequence[SymbolReference]] = asrt.anything_goes(),
        primitive_value: Assertion[FilesCondition] = asrt.anything_goes(),
        symbols: SymbolTable = None
) -> Assertion[SymbolDependentValue]:
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
        references: Assertion[Sequence[SymbolReference]] = asrt.anything_goes(),
        primitive_value: Assertion[StringTransformer] = asrt.anything_goes(),
        symbols: SymbolTable = None
) -> Assertion[SymbolDependentValue]:
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


def matches_sdv_of_program(references: Assertion[Sequence[SymbolReference]],
                           primitive_value: Callable[[TestCaseDs], Assertion[Program]],
                           symbols: Optional[SymbolTable] = None
                           ) -> Assertion[SymbolDependentValue]:
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


def matches_sdv_of_program_constant(references: Assertion[Sequence[SymbolReference]],
                                    primitive_value: Assertion[Program],
                                    symbols: Optional[SymbolTable] = None
                                    ) -> Assertion[SymbolDependentValue]:
    return matches_sdv_of_program(
        references,
        lambda tcds: primitive_value,
        symbols
    )
