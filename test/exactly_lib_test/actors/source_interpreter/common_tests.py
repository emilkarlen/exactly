import unittest

from exactly_lib.test_case.actor import Actor
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib_test.actors.test_resources.act_phase_execution import Arrangement, Expectation, \
    check_execution
from exactly_lib_test.symbol.data.test_resources.path import ConstantSuffixPathDdvSymbolContext
from exactly_lib_test.symbol.test_resources.string import StringConstantSymbolContext
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as pr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions import value_assertion_str as str_asrt


def suite_for(parser_that_executes_python_program: Actor,
              is_shell: bool) -> unittest.TestSuite:
    return unittest.TestSuite([
        TestThatSymbolReferencesAreReportedAndUsed(parser_that_executes_python_program, is_shell),
        TestThatSourceCanReferenceSymbolsThatAreResolvedPostSds(parser_that_executes_python_program, is_shell),
    ])


class TestCaseBase(unittest.TestCase):
    def __init__(self,
                 actor_that_executes_python_program: Actor,
                 is_shell: bool,
                 ):
        super().__init__()
        self.actor_that_executes_python_program = actor_that_executes_python_program
        self.is_shell = is_shell

    def shortDescription(self):
        return '{}, is_shell={}'.format(
            str(type(self)),
            self.is_shell,
        )

    def _check(self,
               source_line: str,
               arrangement: Arrangement,
               expectation: Expectation):
        check_execution(self,
                        self.actor_that_executes_python_program,
                        [instr([source_line])],
                        arrangement,
                        expectation)


class TestThatSymbolReferencesAreReportedAndUsed(TestCaseBase):
    def runTest(self):
        symbol = StringConstantSymbolContext('symbol_name', 'the symbol value')

        program_that_prints_value_of_symbol = 'print("{symbol}")'

        single_source_line = program_that_prints_value_of_symbol.format(
            symbol=symbol.name__sym_ref_syntax,
        )

        expected_output = symbol.str_value + '\n'

        self._check(
            single_source_line,
            Arrangement(
                symbol_table=symbol.symbol_table
            ),
            Expectation(
                symbol_usages=asrt.matches_sequence([
                    symbol.reference_assertion__any_data_type,
                ]),
                sub_process_result_from_execute=pr.stdout(asrt.Equals(expected_output,
                                                                      'program output')),
            ))


class TestThatSourceCanReferenceSymbolsThatAreResolvedPostSds(TestCaseBase):
    def runTest(self):
        symbol = ConstantSuffixPathDdvSymbolContext('symbol_name',
                                                    RelOptionType.REL_ACT,
                                                    'the-path-suffix')

        program_that_prints_value_of_symbol = 'print("{symbol}")'

        single_source_line = program_that_prints_value_of_symbol.format(
            symbol=symbol.name__sym_ref_syntax,
        )

        self._check(
            single_source_line,
            Arrangement(
                symbol_table=symbol.symbol_table

            ),
            Expectation(
                symbol_usages=asrt.matches_singleton_sequence(symbol.reference_assertion__any_data_type),
                sub_process_result_from_execute=pr.stdout(str_asrt.contains(symbol.path_suffix)),
            ))
