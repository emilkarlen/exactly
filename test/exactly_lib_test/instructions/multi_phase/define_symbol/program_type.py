import unittest

from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.multi_phase.define_symbol.test_case_base import TestCaseBaseForParser
from exactly_lib_test.instructions.multi_phase.define_symbol.test_resources import *
from exactly_lib_test.instructions.multi_phase.test_resources.instruction_embryo_check import Expectation
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.symbol.test_resources import sdv_assertions as asrt_sdv
from exactly_lib_test.symbol.test_resources import sdv_structure_assertions as asrt_rs
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.symbol.test_resources.program import is_program_reference_to
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.test_case_file_structure.test_resources import dir_dep_value_assertions as asrt_dir_dep_val
from exactly_lib_test.test_case_utils.program.test_resources import arguments_building as pgm_args
from exactly_lib_test.test_case_utils.program.test_resources import command_cmd_line_args as sym_ref_args
from exactly_lib_test.test_case_utils.program.test_resources import program_sdvs
from exactly_lib_test.test_resources.test_utils import NIE
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.test_resources.program_assertions import \
    matches_py_source_on_cmd_line_program
from exactly_lib_test.util.test_resources.symbol_table_assertions import assert_symbol_table_is_singleton


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSuccessfulDefinition),
    ])


class TestSuccessfulDefinition(TestCaseBaseForParser):
    def test_assignment_of_program_without_arguments(self):
        python_source = 'exit(72)'

        sdv_of_referred_program = program_sdvs.for_py_source_on_command_line(python_source)

        name_of_defined_symbol = 'the_symbol'

        referred_symbol = NameAndValue(
            'PRE_EXISTING_PROGRAM_SYMBOL',
            sdv_of_referred_program
        )

        symbols = SymbolTable({
            referred_symbol.name:
                symbol_utils.container(referred_symbol.value)
        })

        program = pgm_args.symbol_ref_command_line(sym_ref_args.sym_ref_cmd_line(
            referred_symbol.name))

        argument_cases = [
            NIE('value on same line',
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

        for argument_case in argument_cases:
            with self.subTest(argument_case.name):
                expected_symbol_container = asrt_rs.matches_container(
                    assertion_on_sdv=asrt_sdv.matches_sdv_of_program(
                        references=asrt.matches_sequence([
                            is_program_reference_to(referred_symbol.name)
                        ]),
                        resolved_program_value=asrt_dir_dep_val.matches_dir_dependent_value__with_adv(
                            lambda tcds: matches_py_source_on_cmd_line_program(python_source)),
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
                self._check(argument_case.input_value, ArrangementWithSds(), expectation)
