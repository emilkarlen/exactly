import pathlib
import unittest

from exactly_lib.instructions.configuration import timeout as sut
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

    def test_fail_when_more_than_one_argument(self):
        source = new_source2('arg1 arg2')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().apply(source)

    def test_fail_when_a_single_argument_but_that_argument_is_not_an_integer(self):
        source = new_source2('notAnInteger')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().apply(source)

    def test_fail_when_a_single_argument_which_is_an_integer_but_the_value_is_negative(self):
        source = new_source2('-1')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().apply(source)


class TestCaseBaseForParser(TestCaseBase):
    def _run(self,
             expected: int,
             argument: str):
        initial_configuration_builder = ConfigurationBuilder(pathlib.Path(),
                                                             act_phase_handling_that_runs_constant_actions())
        initial_configuration_builder.set_timeout_in_seconds(None)
        self._check(sut.Parser(),
                    new_source2(argument),
                    Arrangement(initial_configuration_builder=initial_configuration_builder),
                    Expectation(configuration=AssertTimeout(expected)))


class TestSetTimeout(TestCaseBaseForParser):
    def test_5(self):
        self._run(expected=5,
                  argument='5')

    def test_75(self):
        self._run(expected=75,
                  argument='75')


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


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParse),
        unittest.makeSuite(TestSetTimeout),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
    ])


if __name__ == '__main__':
    unittest.main()
