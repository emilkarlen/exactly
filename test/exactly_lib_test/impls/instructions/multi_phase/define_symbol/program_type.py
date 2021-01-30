import unittest

from exactly_lib.impls.instructions.multi_phase.define_symbol import parser as sut
from exactly_lib.symbol.value_type import LogicValueType
from exactly_lib_test.impls.instructions.multi_phase.define_symbol.test_resources.abstract_syntax import \
    DefineSymbolWMandatoryValue
from exactly_lib_test.impls.instructions.multi_phase.define_symbol.test_resources.embryo_checker import \
    INSTRUCTION_CHECKER
from exactly_lib_test.impls.instructions.multi_phase.define_symbol.test_resources.source_formatting import *
from exactly_lib_test.impls.instructions.multi_phase.test_resources.instruction_embryo_check import \
    MultiSourceExpectation
from exactly_lib_test.impls.types.program.test_resources import program_sdvs
from exactly_lib_test.impls.types.string_transformer.test_resources.abstract_syntaxes import \
    symbol_reference_followed_by_superfluous_string_on_same_line
from exactly_lib_test.section_document.test_resources import parse_checker
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.dep_variants.test_resources import type_sdv_assertions
from exactly_lib_test.type_val_deps.sym_ref.test_resources.container_assertions import matches_container_of_logic_type
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntax import ProgramOfSymbolReferenceAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntaxes import \
    FullProgramAbsStx, CustomPgmAndArgsAbsStx
from exactly_lib_test.type_val_deps.types.test_resources.program import ProgramSymbolContext
from exactly_lib_test.type_val_prims.program.test_resources.program_assertions import \
    matches_py_source_on_cmd_line_program
from exactly_lib_test.util.test_resources.symbol_table_assertions import assert_symbol_table_is_singleton


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestSuccessfulDefinitionOfProgramWoArguments(),
        TestSuperfluousArguments(),
        TestMissingValue(),
    ])


class TestSuccessfulDefinitionOfProgramWoArguments(unittest.TestCase):
    def runTest(self):
        python_source = 'exit(72)'

        name_of_defined_symbol = 'the_symbol'

        referred_symbol = ProgramSymbolContext.of_sdv(
            'PRE_EXISTING_PROGRAM_SYMBOL',
            program_sdvs.for_py_source_on_command_line(python_source)
        )

        symbols = referred_symbol.symbol_table

        program_abs_stx = ProgramOfSymbolReferenceAbsStx(referred_symbol.name)

        define_symbol_syntax = DefineSymbolWMandatoryValue(
            name_of_defined_symbol,
            ValueType.PROGRAM,
            program_abs_stx,
        )

        expected_symbol_container = matches_container_of_logic_type(
            LogicValueType.PROGRAM,
            sdv=type_sdv_assertions.matches_sdv_of_program_constant(
                references=asrt.matches_sequence([
                    referred_symbol.reference_assertion
                ]),
                primitive_value=matches_py_source_on_cmd_line_program(python_source),
                symbols=symbols
            ))
        expectation = MultiSourceExpectation(
            symbol_usages=asrt.matches_sequence([
                asrt_sym_usage.matches_definition(
                    name=asrt.equals(name_of_defined_symbol),
                    container=expected_symbol_container)
            ]),
            symbols_after_main=assert_symbol_table_is_singleton(
                expected_name=name_of_defined_symbol,
                value_assertion=expected_symbol_container,
            )
        )
        INSTRUCTION_CHECKER.check__abs_stx__layout_and_source_variants(
            self,
            define_symbol_syntax,
            ArrangementWithSds(),
            expectation,
        )


class TestSuperfluousArguments(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        program_w_superfluous_stx = FullProgramAbsStx(
            ProgramOfSymbolReferenceAbsStx('PROGRAM_SYMBOL_NAME'),
            transformation=symbol_reference_followed_by_superfluous_string_on_same_line('TRANSFORMER_SYMBOL_NAME')
        )

        define_symbol_syntax = DefineSymbolWMandatoryValue(
            'the_symbol',
            ValueType.PROGRAM,
            program_w_superfluous_stx,
        )

        PARSE_CHECKER.check_invalid_syntax__src_var_consume_last_line_abs_stx(self, define_symbol_syntax)


class TestMissingValue(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        program_w_superfluous_stx = CustomPgmAndArgsAbsStx(TokenSequence.empty())

        define_symbol_syntax = DefineSymbolWMandatoryValue(
            'the_symbol',
            ValueType.PROGRAM,
            program_w_superfluous_stx,
        )

        PARSE_CHECKER.check_invalid_syntax__abs_stx(self, define_symbol_syntax)


PARSE_CHECKER = parse_checker.Checker(sut.EmbryoParser())
