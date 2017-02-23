import unittest

from exactly_lib.processing.preprocessor import PreprocessorViaExternalProgram
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_suite.instruction_set.sections.configuration import preprocessor as sut
from exactly_lib.test_suite.instruction_set.sections.configuration.instruction_definition import \
    ConfigurationSectionInstruction
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.test_resources.parse import remaining_source
from exactly_lib_test.test_suite.instruction_set.sections.configuration.test_resources import \
    configuration_section_environment


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFailingParse),
        unittest.makeSuite(TestSuccessfulParseAndInstructionExecution),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction mame')),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())


class TestFailingParse(unittest.TestCase):
    def test_fail_when_there_is_no_arguments(self):
        source = remaining_source('   ')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().parse(source)

    def test_fail_when_the_quoting_is_invalid(self):
        source = remaining_source('argument-1 "argument-2')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().parse(source)


class TestSuccessfulParseAndInstructionExecution(unittest.TestCase):
    def _check(self, instruction_argument_source: str,
               expected_command_and_arguments: list):
        # ARRANGE #
        source = remaining_source(instruction_argument_source)
        instruction = sut.Parser().parse(source)
        assert isinstance(instruction, ConfigurationSectionInstruction)
        environment = configuration_section_environment()
        # ACT #
        instruction.execute(environment)
        # ASSERT #
        actual_preprocessor = environment.preprocessor
        self.assertIsInstance(actual_preprocessor, PreprocessorViaExternalProgram)
        assert isinstance(actual_preprocessor, PreprocessorViaExternalProgram)
        self.assertEqual(expected_command_and_arguments,
                         actual_preprocessor.external_program)

    def test_single_command(self):
        self._check('executable', ['executable'])

    def test_command_with_arguments(self):
        self._check('executable arg1 --arg2',
                    ['executable', 'arg1', '--arg2'])

    def test_quoting(self):
        self._check("'executable with space' arg2 \"arg 3\"",
                    ['executable with space', 'arg2', 'arg 3'])
