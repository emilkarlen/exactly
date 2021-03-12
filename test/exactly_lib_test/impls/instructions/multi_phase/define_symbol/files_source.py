import pathlib
import unittest
from typing import Sequence

from exactly_lib.impls.types.files_source.defs import ModificationType
from exactly_lib.impls.types.files_source.impl import literal
from exactly_lib.impls.types.files_source.impl.file_makers.regular import RegularFileMaker
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_val_deps.types.files_source.sdv import FilesSourceSdv
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.parse.token import QuoteType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.impls.instructions.multi_phase.define_symbol.test_resources.abstract_syntax import \
    DefineSymbolWMandatoryValue
from exactly_lib_test.impls.instructions.multi_phase.define_symbol.test_resources.embryo_checker import \
    INSTRUCTION_CHECKER, PARSE_CHECKER
from exactly_lib_test.impls.instructions.multi_phase.define_symbol.test_resources.source_formatting import *
from exactly_lib_test.impls.instructions.multi_phase.test_resources.embryo_arr_exp import Arrangement, Expectation
from exactly_lib_test.impls.types.files_source.test_resources import abstract_syntaxes as abs_stx
from exactly_lib_test.impls.types.files_source.test_resources import integration_check as file_src_check
from exactly_lib_test.impls.types.files_source.test_resources.abstract_syntaxes import LiteralFilesSourceAbsStx
from exactly_lib_test.impls.types.logic.test_resources import intgr_arr_exp
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import ExecutionExpectation
from exactly_lib_test.impls.types.string_source.test_resources.abstract_syntaxes import StringSourceOfStringAbsStx
from exactly_lib_test.symbol.test_resources import symbol_syntax
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.tcfs.test_resources.ds_construction import TcdsArrangement
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import FileSystemElements
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.abstract_syntax_impls import CustomAbsStx
from exactly_lib_test.test_resources.source.custom_abstract_syntax import SequenceAbsStx
from exactly_lib_test.test_resources.value_assertions import file_assertions as asrt_fs
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.dep_variants.test_resources import type_sdv_assertions
from exactly_lib_test.type_val_deps.sym_ref.test_resources.container_assertions import matches_container
from exactly_lib_test.type_val_deps.types.files_source.test_resources.symbol_context import FilesSourceSymbolContext
from exactly_lib_test.type_val_deps.types.string_.test_resources.abstract_syntaxes import MISSING_END_QUOTE__SOFT, \
    StringLiteralAbsStx
from exactly_lib_test.type_val_prims.string_source.test_resources import string_sources
from exactly_lib_test.util.test_resources.symbol_table_assertions import assert_symbol_table_is_singleton


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSuccessfulScenarios),
        unittest.makeSuite(TestUnsuccessfulScenarios),
    ])


class TestSuccessfulScenarios(unittest.TestCase):
    def test_reference(self):
        # ARRANGE #
        defined_name = symbol_syntax.A_VALID_SYMBOL_NAME
        create_file = fs.File('created-file.txt',
                              'contents of created file')

        referenced_symbol = FilesSourceSymbolContext.of_primitive(
            'referenced_name',
            literal.Literal([
                literal.FileSpecification(
                    create_file.name,
                    RegularFileMaker(
                        ModificationType.CREATE,
                        string_sources.of_string(create_file.contents),
                        None,
                    ),
                ),
            ]),
        )
        instruction_syntax = _syntax_of(
            referenced_symbol.abstract_syntax,
            defined_name,
        )

        arrangement = Arrangement.phase_agnostic()

        # EXPECTATION #

        expectation = _expect_definition_of(
            defined_name,
            referenced_symbol.symbol_table,
            (),
            referenced_symbol.references_assertion,
            asrt_fs.dir_contains_exactly_2([create_file])
        )

        # ACT & ASSERT #

        INSTRUCTION_CHECKER.check__abs_stx__std_layouts_and_source_variants(
            self,
            instruction_syntax,
            arrangement,
            expectation,
        )

    def test_literal(self):
        # ARRANGE #
        defined_name = symbol_syntax.A_VALID_SYMBOL_NAME
        create_file = fs.File('created-file.txt',
                              'contents of created file')

        literal_syntax = abs_stx.LiteralFilesSourceAbsStx([
            abs_stx.regular_file_spec(
                StringLiteralAbsStx(create_file.name, QuoteType.HARD),
                abs_stx.FileContentsExplicitAbsStx(
                    ModificationType.CREATE,
                    StringSourceOfStringAbsStx.of_str(create_file.contents,
                                                      QuoteType.HARD),
                )
            )
        ])
        syntax = _syntax_of(
            literal_syntax,
            defined_name,
        )

        arrangement = Arrangement.phase_agnostic()

        # EXPECTATION #

        expectation = _expect_definition_of(
            defined_name,
            SymbolTable.empty(),
            (),
            asrt.is_empty_sequence,
            asrt_fs.dir_contains_exactly_2([create_file])
        )

        # ACT & ASSERT #

        INSTRUCTION_CHECKER.check__abs_stx__std_layouts_and_source_variants(
            self,
            syntax,
            arrangement,
            expectation,
        )


class TestUnsuccessfulScenarios(unittest.TestCase):
    def test_failing_parse(self):
        cases = [
            NameAndValue(
                'missing argument',
                CustomAbsStx.empty(),
            ),
            NameAndValue(
                'missing end quote in file name',
                LiteralFilesSourceAbsStx([
                    abs_stx.regular_file_spec(
                        MISSING_END_QUOTE__SOFT,
                        abs_stx.FileContentsEmptyAbsStx(),
                    )
                ])
            ),
            NameAndValue(
                'superfluous arguments',
                SequenceAbsStx.followed_by_superfluous(
                    LiteralFilesSourceAbsStx([])
                ),
            ),
        ]
        # ARRANGE #
        for case in cases:
            with self.subTest(case.name):
                PARSE_CHECKER.check_invalid_syntax__abs_stx(
                    self,
                    _syntax_of(case.value)
                )


def _syntax_of(string_source: AbstractSyntax,
               defined_name: str = symbol_syntax.A_VALID_SYMBOL_NAME) -> AbstractSyntax:
    return DefineSymbolWMandatoryValue(
        defined_name,
        ValueType.FILES_SOURCE,
        string_source,
    )


def _expect_definition_of(
        defined_name: str,
        symbols_for_evaluation: SymbolTable,
        model: FileSystemElements,
        references: Assertion[Sequence[SymbolReference]],
        expected_output: Assertion[pathlib.Path],
) -> Expectation[pathlib.Path]:
    sdv_expectation = type_sdv_assertions.matches_sdv(
        asrt.is_instance(FilesSourceSdv),
        references=references,
        symbols=symbols_for_evaluation,
        resolved_value=asrt.anything_goes(),
        custom=asrt.is_instance_with(
            FilesSourceSdv,
            file_src_check.execution_assertion(
                model,
                intgr_arr_exp.Arrangement(
                    symbols=symbols_for_evaluation,
                    tcds=TcdsArrangement(),
                ),
                ExecutionExpectation(
                    main_result=expected_output,
                )
            ),
        )
    )
    expected_container = matches_container(
        asrt.equals(ValueType.FILES_SOURCE),
        sdv_expectation,
    )
    return Expectation.phase_agnostic(
        symbol_usages=asrt.matches_sequence([
            asrt_sym_usage.matches_definition(asrt.equals(defined_name),
                                              expected_container),
        ]),
        symbols_after_main=assert_symbol_table_is_singleton(
            defined_name,
            expected_container,
        )
    )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
