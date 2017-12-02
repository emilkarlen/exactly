import unittest

from exactly_lib.instructions.configuration import timeout as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case.phases.configuration import ConfigurationBuilder
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
        unittest.makeSuite(TestFailingParse),
        unittest.makeSuite(TestSetTimeout),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
    ])


class TestFailingParse(unittest.TestCase):
    def test(self):
        cases = [
            '   ',
            'arg1 arg2',
            'notAnInteger',
            '-1',
            '=5',
        ]
        for argument_str in cases:
            with self.subTest(argument_str):
                for source in equivalent_source_variants(self, argument_str):
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        sut.Parser().parse(source)


class TestCaseBaseForParser(TestCaseBase):
    def _run(self,
             expected: int,
             argument: str):
        for source in equivalent_source_variants__with_source_check(self, argument):
            self._check(sut.Parser(),
                        source,
                        Arrangement(
                            act_phase_handling=act_phase_handling_that_runs_constant_actions(),
                            timeout_in_seconds=None),
                        Expectation(
                            configuration=AssertTimeout(expected)))


class TestSetTimeout(TestCaseBaseForParser):
    def test_5(self):
        self._run(expected=5,
                  argument='= 5')

    def test_75(self):
        self._run(expected=75,
                  argument='  = 75')


class AssertTimeout(config_check.Assertion):
    def __init__(self,
                 expected: int):
        self.expected = expected

    def apply(self,
              put: unittest.TestCase,
              initial: ConfigurationBuilder,
              actual_result: ConfigurationBuilder):
        put.assertEqual(self.expected,
                        actual_result.timeout_in_seconds,
                        'timeout')


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
