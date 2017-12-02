import unittest

import exactly_lib.test_case.test_case_status
from exactly_lib.instructions.configuration import test_case_status as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case.phases.configuration import ConfigurationBuilder
from exactly_lib.test_case.test_case_status import ExecutionMode
from exactly_lib_test.execution.test_resources.act_source_executor import act_phase_handling_that_runs_constant_actions
from exactly_lib_test.instructions.configuration.test_resources import configuration_check as config_check
from exactly_lib_test.instructions.configuration.test_resources.instruction_check import TestCaseBase, \
    Arrangement, Expectation
from exactly_lib_test.instructions.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants, \
    equivalent_source_variants__with_source_check


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParse),
        unittest.makeSuite(TestChangeMode),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
    ])


class TestParse(unittest.TestCase):
    def test_fail_when_there_is_no_arguments(self):
        for source in equivalent_source_variants(self, '   '):
            with self.assertRaises(SingleInstructionInvalidArgumentException):
                sut.Parser().parse(source)

    def test_fail_when_the_argument_is_invalid(self):
        for source in equivalent_source_variants(self, 'invalid-argument'):
            with self.assertRaises(SingleInstructionInvalidArgumentException):
                sut.Parser().parse(source)


class TestCaseBaseForParser(TestCaseBase):
    def _run(self,
             expected: ExecutionMode,
             initial: ExecutionMode,
             argument: str):
        for source in equivalent_source_variants__with_source_check(self, argument):
            self._check(sut.Parser(),
                        source,
                        Arrangement(execution_mode=initial,
                                    act_phase_handling=act_phase_handling_that_runs_constant_actions()),
                        Expectation(configuration=AssertExecutionMode(expected)))


class TestChangeMode(TestCaseBaseForParser):
    def test_NORMAL(self):
        self._run(expected=ExecutionMode.PASS,
                  initial=ExecutionMode.SKIP,
                  argument=exactly_lib.test_case.test_case_status.NAME_PASS)

    def test_SKIP(self):
        self._run(expected=ExecutionMode.SKIP,
                  initial=ExecutionMode.PASS,
                  argument=exactly_lib.test_case.test_case_status.NAME_SKIP)

    def test_XFAIL(self):
        self._run(expected=ExecutionMode.FAIL,
                  initial=ExecutionMode.PASS,
                  argument=exactly_lib.test_case.test_case_status.NAME_FAIL)


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


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
