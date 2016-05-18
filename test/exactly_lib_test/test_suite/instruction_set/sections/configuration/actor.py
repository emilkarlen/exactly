import unittest

from exactly_lib.act_phase_setups.script_language_setup import ActProgramExecutorForScriptLanguage
from exactly_lib.script_language.script_language_management import ScriptLanguageSetup
from exactly_lib.script_language.standard_script_language import StandardScriptLanguage, StandardScriptFileManager
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case.phases.act.phase_setup import ActPhaseSetup
from exactly_lib.test_suite.instruction_set.sections.configuration import actor as sut
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.test_resources.parse import new_source2
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
        source = new_source2('   ')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().apply(source)

    def test_fail_when_the_quoting_is_invalid(self):
        source = new_source2('argument-1 "argument-2')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().apply(source)


class TestSuccessfulParseAndInstructionExecution(unittest.TestCase):
    def _check(self, instruction_argument_source: str,
               expected_command_and_arguments: list):
        # Quite bad test, since it checks too many internal details.
        # It should instead test the behaviour of the act-phase-setup
        # by executing it.

        # ARRANGE #
        source = new_source2(instruction_argument_source)
        instruction = sut.Parser().apply(source)
        environment = configuration_section_environment()
        # ACT #
        instruction.execute(environment)
        # ASSERT #
        act_phase_setup = environment.act_phase_setup
        self.assertIsInstance(act_phase_setup, ActPhaseSetup)
        assert isinstance(act_phase_setup, ActPhaseSetup)
        executor = act_phase_setup.executor
        self.assertIsInstance(executor,
                              ActProgramExecutorForScriptLanguage)
        assert isinstance(executor, ActProgramExecutorForScriptLanguage)
        script_language_setup = executor.script_language_setup
        self.assertIsInstance(script_language_setup,
                              ScriptLanguageSetup)
        assert isinstance(script_language_setup, ScriptLanguageSetup)
        language = script_language_setup.language
        self.assertIsInstance(language,
                              StandardScriptLanguage)
        assert isinstance(language, StandardScriptLanguage)
        file_manager = script_language_setup.file_manager
        self.assertIsInstance(file_manager,
                              StandardScriptFileManager)
        assert isinstance(file_manager, StandardScriptFileManager)
        self.assertEqual([file_manager.interpreter] + file_manager.command_line_options_before_file_argument,
                         expected_command_and_arguments)

    def test_single_command(self):
        self._check('executable', ['executable'])

    def test_command_with_arguments(self):
        self._check('executable arg1 --arg2',
                    ['executable', 'arg1', '--arg2'])

    def test_quoting(self):
        self._check("'executable with space' arg2 \"arg 3\"",
                    ['executable with space', 'arg2', 'arg 3'])
