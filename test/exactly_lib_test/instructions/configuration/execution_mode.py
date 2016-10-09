import pathlib
import unittest

import exactly_lib.execution.execution_mode
from exactly_lib.execution.execution_mode import ExecutionMode
from exactly_lib.instructions.configuration import execution_mode as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case.phases.configuration import ConfigurationBuilder
from exactly_lib_test.execution.test_resources.act_source_executor import act_phase_handling_that_runs_constant_actions
from exactly_lib_test.instructions.configuration.test_resources import configuration_check as config_check
from exactly_lib_test.instructions.configuration.test_resources.instruction_check import TestCaseBase, \
    Arrangement, Expectation
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.test_resources.parse import new_source2


class TestParse(unittest.TestCase):
    def test_fail_when_there_is_no_arguments(self):
        source = new_source2('   ')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().apply(source)

    def test_fail_when_the_argument_is_invalid(self):
        source = new_source2('invalid-argument')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().apply(source)


class TestCaseBaseForParser(TestCaseBase):
    def _run(self,
             expected: ExecutionMode,
             initial: ExecutionMode,
             argument: str):
        initial_configuration_builder = ConfigurationBuilder(pathlib.Path(),
                                                             act_phase_handling_that_runs_constant_actions())
        initial_configuration_builder.set_execution_mode(initial)
        self._check(sut.Parser(),
                    new_source2(argument),
                    Arrangement(initial_configuration_builder=initial_configuration_builder),
                    Expectation(configuration=AssertExecutionMode(expected)))


class TestChangeMode(TestCaseBaseForParser):
    def test_NORMAL(self):
        self._run(expected=ExecutionMode.NORMAL,
                  initial=ExecutionMode.SKIP,
                  argument=exactly_lib.execution.execution_mode.NAME_NORMAL)

    def test_SKIP(self):
        self._run(expected=ExecutionMode.SKIP,
                  initial=ExecutionMode.NORMAL,
                  argument=exactly_lib.execution.execution_mode.NAME_SKIP)

    def test_XFAIL(self):
        self._run(expected=ExecutionMode.XFAIL,
                  initial=ExecutionMode.NORMAL,
                  argument=exactly_lib.execution.execution_mode.NAME_XFAIL)


class AssertExecutionMode(config_check.Assertion):
    def __init__(self,
                 expected: ExecutionMode):
        self.expected = expected

    def apply(self,
              put: unittest.TestCase,
              initial: ConfigurationBuilder,
              actual_result: ConfigurationBuilder):
        put.assertEqual(self.expected,
                        actual_result.execution_mode,
                        'Execution Mode')


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParse),
        unittest.makeSuite(TestChangeMode),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
    ])


if __name__ == '__main__':
    unittest.main()
