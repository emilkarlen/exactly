import unittest

from exactly_lib.act_phase_setups.util.executor_made_of_parts import parts
from exactly_lib.symbol.restrictions.reference_restrictions import no_restrictions
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.parse.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.type_system_values import file_refs
from exactly_lib.type_system_values.concrete_path_parts import PathPartAsFixedPath
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.act_phase_setups.test_resources.act_phase_execution import Arrangement, Expectation, \
    check_execution
from exactly_lib_test.symbol.test_resources import symbol_utils as su
from exactly_lib_test.symbol.test_resources.symbol_reference_assertions import equals_symbol_references
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as pr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions import value_assertion_str as str_asrt


def suite_for(constructor_that_executes_python_program: parts.Constructor,
              is_shell: bool) -> unittest.TestSuite:
    return unittest.TestSuite([
        TestThatSymbolReferencesAreReportedAndUsed(constructor_that_executes_python_program, is_shell),
        TestThatSourceCanReferenceSymbolsThatAreResolvedPostSds(constructor_that_executes_python_program, is_shell),
    ])


class TestCaseBase(unittest.TestCase):
    def __init__(self, constructor_that_executes_python_program: parts.Constructor,
                 is_shell: bool):
        super().__init__()
        self.constructor_that_executes_python_program = constructor_that_executes_python_program
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
                        self.constructor_that_executes_python_program,
                        [instr([source_line])],
                        arrangement,
                        expectation)


class TestThatSymbolReferencesAreReportedAndUsed(TestCaseBase):
    def runTest(self):
        symbol = NameAndValue('symbol_name', 'the symbol value')

        program_that_prints_value_of_symbol = 'print("{symbol}")'

        single_source_line = program_that_prints_value_of_symbol.format(
            symbol=symbol_reference_syntax_for_name(symbol.name),
        )

        expected_output = symbol.value + '\n'

        self._check(
            single_source_line,
            Arrangement(
                symbol_table=SymbolTable({
                    symbol.name:
                        su.string_value_constant_container(symbol.value),
                })

            ),
            Expectation(
                symbol_usages=equals_symbol_references([
                    SymbolReference(symbol.name,
                                    no_restrictions()),
                ]),
                sub_process_result_from_execute=pr.stdout(asrt.Equals(expected_output,
                                                                      'program output')),
            ))


class TestThatSourceCanReferenceSymbolsThatAreResolvedPostSds(TestCaseBase):
    def runTest(self):
        path_suffix = 'the-path-suffix'
        symbol = NameAndValue('symbol_name',
                              file_refs.rel_act(PathPartAsFixedPath(path_suffix)))

        program_that_prints_value_of_symbol = 'print("{symbol}")'

        single_source_line = program_that_prints_value_of_symbol.format(
            symbol=symbol_reference_syntax_for_name(symbol.name),
        )

        self._check(
            single_source_line,
            Arrangement(
                symbol_table=SymbolTable({
                    symbol.name:
                        su.file_ref_constant_container(symbol.value),
                })

            ),
            Expectation(
                symbol_usages=equals_symbol_references([
                    SymbolReference(symbol.name,
                                    no_restrictions()),
                ]),
                sub_process_result_from_execute=pr.stdout(str_asrt.contains(path_suffix)),
            ))
