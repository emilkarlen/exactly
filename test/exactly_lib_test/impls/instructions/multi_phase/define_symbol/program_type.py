import unittest

from exactly_lib.impls.instructions.multi_phase.define_symbol import parser as sut
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.value_type import LogicValueType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.instructions.multi_phase.define_symbol.test_resources.embryo_checker import \
    INSTRUCTION_CHECKER
from exactly_lib_test.impls.instructions.multi_phase.define_symbol.test_resources.source_formatting import *
from exactly_lib_test.impls.instructions.multi_phase.test_resources.instruction_embryo_check import Expectation
from exactly_lib_test.impls.types.program.test_resources import arguments_building as pgm_args
from exactly_lib_test.impls.types.program.test_resources import command_cmd_line_args as sym_ref_args
from exactly_lib_test.impls.types.program.test_resources import program_sdvs
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.test_resources.test_utils import NIE
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.dep_variants.test_resources import type_sdv_assertions
from exactly_lib_test.type_val_deps.sym_ref.test_resources.container_assertions import matches_container_of_logic_type
from exactly_lib_test.type_val_deps.types.test_resources.program import ProgramSymbolContext
from exactly_lib_test.type_val_prims.program.test_resources.program_assertions import \
    matches_py_source_on_cmd_line_program
from exactly_lib_test.util.test_resources.symbol_table_assertions import assert_symbol_table_is_singleton


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSuccessfulDefinition),
        unittest.makeSuite(TestInvalidSyntax),
    ])


class TestSuccessfulDefinition(unittest.TestCase):
    def test_assignment_of_program_without_arguments(self):
        python_source = 'exit(72)'

        name_of_defined_symbol = 'the_symbol'

        referred_symbol = ProgramSymbolContext.of_sdv(
            'PRE_EXISTING_PROGRAM_SYMBOL',
            program_sdvs.for_py_source_on_command_line(python_source)
        )

        symbols = referred_symbol.symbol_table

        program = pgm_args.symbol_ref_command_line(sym_ref_args.sym_ref_cmd_line(
            referred_symbol.name))

        program_value_location_cases = [
            NIE('value on one and only line',
                asrt_source.source_is_at_end,
                multi_line_source('{program_type} {defined_symbol} = {program}',
                                  [],
                                  defined_symbol=name_of_defined_symbol,
                                  program=program)
                ),
            NIE('value on same line / followed by empty line',
                asrt_source.is_at_beginning_of_line(2),
                multi_line_source('{program_type} {defined_symbol} = {program}',
                                  [''],
                                  defined_symbol=name_of_defined_symbol,
                                  program=program)
                ),
            NIE('value on same line / followed by non-empty line',
                asrt_source.is_at_beginning_of_line(2),
                multi_line_source('{program_type} {defined_symbol} = {program}',
                                  ['following line'],
                                  defined_symbol=name_of_defined_symbol,
                                  program=program)
                ),
            NIE('value on following line',
                asrt_source.is_at_beginning_of_line(3),
                multi_line_source('{program_type} {defined_symbol} =',
                                  ['{program}',
                                   'following line'],
                                  defined_symbol=name_of_defined_symbol,
                                  program=program)
                ),
        ]

        for argument_case in program_value_location_cases:
            with self.subTest(argument_case.name):
                expected_symbol_container = matches_container_of_logic_type(
                    LogicValueType.PROGRAM,
                    sdv=type_sdv_assertions.matches_sdv_of_program_constant(
                        references=asrt.matches_sequence([
                            referred_symbol.reference_assertion
                        ]),
                        primitive_value=matches_py_source_on_cmd_line_program(python_source),
                        symbols=symbols
                    ))
                expectation = Expectation(
                    source=argument_case.expected_value,
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
                INSTRUCTION_CHECKER.check(self, argument_case.input_value, ArrangementWithSds(), expectation)


class TestInvalidSyntax(unittest.TestCase):
    def test_superfluous_arguments(self):
        # ARRANGE #
        program_w_superfluous_args = pgm_args.program_w_superfluous_args()

        name_of_defined_symbol = 'the_symbol'

        program_value_location_cases = [
            NameAndValue('value on same line',
                         multi_line_source('{program_type} {defined_symbol} = {program}',
                                           ['following line'],
                                           defined_symbol=name_of_defined_symbol,
                                           program=program_w_superfluous_args)
                         ),
            NameAndValue('value on following line',
                         multi_line_source('{program_type} {defined_symbol} =',
                                           ['{program}',
                                            'following line'],
                                           defined_symbol=name_of_defined_symbol,
                                           program=program_w_superfluous_args)
                         ),
        ]
        parser = sut.EmbryoParser()
        for argument_case in program_value_location_cases:
            with self.subTest(argument_case.name):
                # ACT & ASSERT #
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    parser.parse(ARBITRARY_FS_LOCATION_INFO, argument_case.value)
