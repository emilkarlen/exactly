import unittest
from typing import List

from exactly_lib_test.impls.instructions.assert_.process_output.exit_code.test_resources.abstract_syntax import \
    InstructionArguments
from exactly_lib_test.impls.instructions.assert_.process_output.exit_code.test_resources.instruction_check import \
    CHECKER
from exactly_lib_test.impls.instructions.assert_.test_resources.instruction_check import Expectation2
from exactly_lib_test.impls.instructions.test_resources.instr_arr_exp import ParseExpectation
from exactly_lib_test.impls.types.integer_matcher.test_resources.abstract_syntaxes import IntegerMatcherInfixOpAbsStx
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct2, ProcessExecutionArrangement
from exactly_lib_test.test_case.test_resources.command_executors import CommandExecutorThatJustReturnsConstant
from exactly_lib_test.test_case.test_resources.os_services import os_services_w_cmd_exe_counting__w_wrapped
from exactly_lib_test.test_resources import recording
from exactly_lib_test.type_val_deps.types.integer_matcher.test_resources.abstract_syntax import IntegerMatcherAbsStx
from exactly_lib_test.type_val_deps.types.test_resources.integer_matcher import IntegerMatcherSymbolContext
from exactly_lib_test.type_val_deps.types.test_resources.program import ProgramSymbolContext


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestProgramIsExecutedEvenThoughMatcherDoNotAccessModel(),
        TestProgramIsExecutedOnceEvenThoughModelIsAccessedMultipleTimes(),
    ])


class TestProgramIsExecutedEvenThoughMatcherDoNotAccessModel(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        integer_matcher_that_do_not_access_model = IntegerMatcherSymbolContext.of_primitive_constant(
            'IM_CONSTANT',
            True,
        )
        # ACT & ASSERT #
        _check(self,
               integer_matcher_that_do_not_access_model.abstract_syntax,
               [integer_matcher_that_do_not_access_model])


class TestProgramIsExecutedOnceEvenThoughModelIsAccessedMultipleTimes(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        const_true__matcher = IntegerMatcherSymbolContext.of_primitive_constant(
            'IM_CONSTANT_TRUE_1',
            True,
        )
        complex_integer_matcher = IntegerMatcherInfixOpAbsStx.conjunction([
            const_true__matcher.abstract_syntax,
            const_true__matcher.abstract_syntax,
        ],
            within_parens=True,
        )
        # ACT & ASSERT #
        _check(self,
               complex_integer_matcher,
               [const_true__matcher, const_true__matcher])


def _check(put: unittest.TestCase,
           integer_matcher: IntegerMatcherAbsStx,
           integer_matcher_symbols: List[SymbolContext]):
    # ARRANGE #
    program_symbol = ProgramSymbolContext.of_arbitrary_value('PROGRAM_SYMBOL')
    all_symbols = [program_symbol] + integer_matcher_symbols

    command_execution_counter = recording.Counter(initial_value=0)
    # ACT & ASSERT #
    CHECKER.check__abs_stx(
        put,
        InstructionArguments(
            program_symbol.abstract_syntax,
            integer_matcher,
        ),
        ArrangementPostAct2(
            symbols=SymbolContext.symbol_table_of_contexts(all_symbols),
            process_execution=ProcessExecutionArrangement(
                os_services=os_services_w_cmd_exe_counting__w_wrapped(
                    command_execution_counter,
                    CommandExecutorThatJustReturnsConstant(1)
                ),
            )
        ),
        Expectation2(
            ParseExpectation(
                symbol_usages=SymbolContext.usages_assertion_of_contexts(all_symbols)
            )
        ),
    )
    put.assertEqual(1,
                    command_execution_counter.value,
                    'number of times the program has been executed')
