import unittest

from exactly_lib.impls.os_services import os_services_access
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib_test.impls.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.impls.instructions.assert_.test_resources.stdout_stderr.program_output import \
    arguments_building as args
from exactly_lib_test.impls.instructions.assert_.test_resources.stdout_stderr.program_output import \
    configuration
from exactly_lib_test.impls.instructions.assert_.test_resources.stdout_stderr.program_output.configuration import \
    TestCaseBase
from exactly_lib_test.impls.types.matcher.test_resources.matchers import MatcherTestImplBase
from exactly_lib_test.impls.types.program.test_resources import arguments_building as pgm_args
from exactly_lib_test.impls.types.string_matcher.test_resources import arguments_building2 as args2
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.test_case.test_resources.command_executors import CommandExecutorWInitialAction
from exactly_lib_test.test_resources import recording
from exactly_lib_test.type_val_deps.types.test_resources.string_matcher import StringMatcherSymbolContext
from exactly_lib_test.type_val_prims.matcher.test_resources import matching_result


def suite_for(conf: configuration.ProgramOutputInstructionConfiguration) -> unittest.TestSuite:
    return unittest.TestSuite([
        TestProgramIsExecutedEvenThoughMatcherDoNotAccessModel(conf),
        TestProgramIsExecutedOnceEvenThoughModelIsAccessedMultipleTimes(conf),
    ])


class TestProgramIsExecutedEvenThoughMatcherDoNotAccessModel(TestCaseBase):
    def runTest(self):
        # ARRANGE #
        program_that_outputs_something = pgm_args.program(
            pgm_args.interpret_py_source_line(
                self.configuration.py_source_for_print('some output')),
        )
        string_matcher_that_do_not_access_model = StringMatcherSymbolContext.of_primitive_constant(
            'SM_CONSTANT',
            True,
        )
        arguments = args.from_program(program_that_outputs_something,
                                      [string_matcher_that_do_not_access_model.name__sym_ref_syntax])

        command_execution_counter = recording.Counter(initial_value=0)
        # ACT & ASSERT #
        self._check(
            arguments,
            ArrangementPostAct(
                symbols=string_matcher_that_do_not_access_model.symbol_table,
                os_services=(_os_services_w_cmd_exe_counting(command_execution_counter)),
            ),
            Expectation(
                symbol_usages=string_matcher_that_do_not_access_model.usages_assertion
            ),
        )
        self.assertEqual(1,
                         command_execution_counter.value,
                         'number of times the program has been executed')


class TestProgramIsExecutedOnceEvenThoughModelIsAccessedMultipleTimes(TestCaseBase):
    def runTest(self):
        # ARRANGE #
        program_that_outputs_something = pgm_args.program(
            pgm_args.interpret_py_source_line(
                self.configuration.py_source_for_print('some output')),
        )
        const_true__matcher_that_accesses_model = StringMatcherSymbolContext.of_primitive(
            'SM_CONSTANT_TRUE',
            _StringMatcherThatAccessesModel(True),
        )
        matcher_w_multiple_accesses = args2.conjunction([
            args2.SymbolReferenceWReferenceSyntax(const_true__matcher_that_accesses_model.name),
            args2.SymbolReferenceWReferenceSyntax(const_true__matcher_that_accesses_model.name),
        ])
        arguments = args.from_program(program_that_outputs_something,
                                      matcher_w_multiple_accesses.elements)

        command_execution_counter = recording.Counter(initial_value=0)
        # ACT & ASSERT #
        self._check(
            arguments,
            ArrangementPostAct(
                symbols=const_true__matcher_that_accesses_model.symbol_table,
                os_services=(_os_services_w_cmd_exe_counting(command_execution_counter)),
            ),
            Expectation(
                symbol_usages=SymbolContext.usages_assertion_of_contexts([
                    const_true__matcher_that_accesses_model,
                    const_true__matcher_that_accesses_model,
                ])
            ),
        )
        self.assertEqual(1,
                         command_execution_counter.value,
                         'number of times the program has been executed')


def _os_services_w_cmd_exe_counting(counter: recording.Counter) -> OsServices:
    os_services__default = os_services_access.new_for_current_os()
    return os_services_access.new_for_cmd_exe(
        CommandExecutorWInitialAction(
            os_services__default.command_executor,
            initial_action=counter.increase,
        )
    )


class _StringMatcherThatAccessesModel(MatcherTestImplBase[StringSource]):
    def __init__(self, result: bool):
        self._result = result

    def matches_w_trace(self, model: StringSource) -> MatchingResult:
        self._access(model)
        return matching_result.of(self._result)

    @staticmethod
    def _access(model: StringSource):
        contents_as_str = model.contents().as_str
