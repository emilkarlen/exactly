import unittest

from exactly_lib.definitions.instruction_arguments import ASSIGNMENT_OPERATOR
from exactly_lib.instructions.configuration import test_case_status as sut
from exactly_lib.section_document.element_parsers.instruction_parser_for_single_section import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case import test_case_status as tcs
from exactly_lib.test_case.phases.configuration import ConfigurationBuilder
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.instructions.configuration.test_resources import configuration_check as config_check
from exactly_lib_test.instructions.configuration.test_resources.instruction_check import TestCaseBase, \
    Arrangement, Expectation
from exactly_lib_test.instructions.configuration.test_resources.source_with_assignment import syntax_for_assignment_of
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants, \
    equivalent_source_variants__with_source_check
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.test_case.act_phase_handling.test_resources.act_phase_handlings import \
    act_phase_handling_that_runs_constant_actions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParse),
        unittest.makeSuite(TestChangeStatus),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
    ])


class TestParse(unittest.TestCase):
    def test_invalid_syntax(self):
        cases = [
            '   ',
            ASSIGNMENT_OPERATOR + ' ',
            ' '.join([ASSIGNMENT_OPERATOR, tcs.NAME_SKIP, tcs.NAME_PASS]),
        ]
        for argument_str in cases:
            with self.subTest(argument_str):
                for source in equivalent_source_variants(self, argument_str):
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        sut.Parser().parse(ARBITRARY_FS_LOCATION_INFO, source)


class TestCaseBaseForParser(TestCaseBase):
    def _run(self,
             expected: tcs.ExecutionMode,
             initial: tcs.ExecutionMode,
             argument: str):
        for source in equivalent_source_variants__with_source_check(self, argument):
            self._check(sut.Parser(),
                        source,
                        Arrangement(execution_mode=initial,
                                    act_phase_handling=act_phase_handling_that_runs_constant_actions()),
                        Expectation(configuration=AssertExecutionMode(expected)))


class TestChangeStatus(TestCaseBaseForParser):
    def test_PASS(self):
        self._run(expected=tcs.ExecutionMode.PASS,
                  initial=tcs.ExecutionMode.SKIP,
                  argument=syntax_for_assignment_of(tcs.NAME_PASS))

    def test_SKIP(self):
        self._run(expected=tcs.ExecutionMode.SKIP,
                  initial=tcs.ExecutionMode.PASS,
                  argument=syntax_for_assignment_of(tcs.NAME_SKIP))

    def test_FAIL(self):
        self._run(expected=tcs.ExecutionMode.FAIL,
                  initial=tcs.ExecutionMode.PASS,
                  argument=syntax_for_assignment_of(tcs.NAME_FAIL))


class AssertExecutionMode(config_check.Assertion):
    def __init__(self,
                 expected: tcs.ExecutionMode):
        self.expected = expected

    def apply(self,
              put: unittest.TestCase,
              initial: ConfigurationBuilder,
              actual_result: ConfigurationBuilder):
        put.assertEqual(self.expected,
                        actual_result.execution_mode,
                        'Test Case Status')


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
