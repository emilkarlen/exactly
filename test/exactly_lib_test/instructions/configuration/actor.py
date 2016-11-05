import pathlib
import unittest

from exactly_lib.act_phase_setups.script_interpretation import script_language_setup
from exactly_lib.act_phase_setups.script_interpretation.script_language_management import ScriptLanguageSetup, \
    StandardScriptFileManager
from exactly_lib.execution.act_phase import ActPhaseHandling, ActSourceAndExecutorConstructor
from exactly_lib.instructions.configuration import actor as sut
from exactly_lib.instructions.configuration.utils import actor_utils
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.configuration import ConfigurationBuilder
from exactly_lib_test.act_phase_setups.test_resources import act_phase_execution
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.test_resources import shell_commands
from exactly_lib_test.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_resources.parse import new_source2
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as pr
from exactly_lib_test.test_resources.value_assertions import value_assertion as va


class TestFailingParseForAnyActor(unittest.TestCase):
    def test_fail_when_there_is_no_arguments(self):
        source = new_source2('   ')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().apply(source)

    def test_fail_when_the_quoting_is_invalid(self):
        source = new_source2('argument-1 "argument-2')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().apply(source)


class TestFailingParseForShellCommand(unittest.TestCase):
    def test_fail_when_extra_unexpected_argument(self):
        source = new_source2(actor_utils.SHELL_COMMAND_ACTOR_KEYWORD + ' extra-unexpected-argument')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().apply(source)


class TestFailingParseForInterpreter(unittest.TestCase):
    def test_fail_when_missing_program_argument(self):
        source = new_source2(actor_utils.INTERPRETER_ACTOR_KEYWORD)
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().apply(source)


class TestSuccessfulParseAndInstructionExecutionForInterpreterActor(unittest.TestCase):
    def _check(self, instruction_argument_source: str,
               expected_command_and_arguments: list):
        # TODO Quite bad test, since it checks too many internal details.
        # It should instead test the behaviour of the act-phase-setup
        # by executing it.

        # ARRANGE #
        source = new_source2(instruction_argument_source)
        instruction = sut.Parser().apply(source)
        # ACT #
        configuration_builder = _configuration_builder_with_exception_throwing_act_phase_setup()
        instruction.main(configuration_builder)
        # ASSERT #
        act_phase_handling = configuration_builder.act_phase_handling
        self.assertIsInstance(act_phase_handling, ActPhaseHandling)
        assert isinstance(act_phase_handling, ActPhaseHandling)
        constructor = act_phase_handling.source_and_executor_constructor
        self.assertIsInstance(constructor,
                              script_language_setup.Constructor)
        language_setup = constructor.script_language_setup
        self.assertIsInstance(language_setup,
                              ScriptLanguageSetup)
        assert isinstance(language_setup, ScriptLanguageSetup)
        file_manager = language_setup.file_manager
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

    def test_with_interpreter_keyword(self):
        self._check(actor_utils.INTERPRETER_ACTOR_KEYWORD + ' executable arg',
                    ['executable', 'arg'])


class TestShellHandlingViaExecution(unittest.TestCase):
    def test_valid_shell_command(self):
        _check(self,
               Arrangement(actor_utils.SHELL_COMMAND_ACTOR_KEYWORD,
                           [shell_commands.command_that_prints_line_to_stdout('output on stdout')]),
               Expectation(sub_process_result_from_execute=pr.stdout(va.Equals('output on stdout',
                                                                               'expected output on stdout')))
               )


class Arrangement:
    def __init__(self,
                 instruction_argument: str,
                 act_phase_source_lines: list):
        self.instruction_argument = instruction_argument
        self.act_phase_source_lines = act_phase_source_lines


class Expectation:
    def __init__(self,
                 sub_process_result_from_execute: va.ValueAssertion = va.anything_goes()):
        self.sub_process_result_from_execute = sub_process_result_from_execute


def _check(put: unittest.TestCase,
           arrangement: Arrangement,
           expectation: Expectation):
    source = new_source2(arrangement.instruction_argument)
    instruction = sut.Parser().apply(source)
    configuration_builder = _configuration_builder_with_exception_throwing_act_phase_setup()
    instruction.main(configuration_builder)
    act_phase_instructions = [instr(arrangement.act_phase_source_lines)]
    executor_constructor = configuration_builder.act_phase_handling.source_and_executor_constructor
    act_phase_execution.check_execution(put,
                                        act_phase_execution.Arrangement(executor_constructor=executor_constructor,
                                                                        act_phase_instructions=act_phase_instructions),
                                        act_phase_execution.Expectation(
                                            sub_process_result_from_execute=expectation.sub_process_result_from_execute)
                                        )


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFailingParseForAnyActor),
        unittest.makeSuite(TestFailingParseForShellCommand),
        unittest.makeSuite(TestFailingParseForInterpreter),
        unittest.makeSuite(TestSuccessfulParseAndInstructionExecutionForInterpreterActor),
        unittest.makeSuite(TestShellHandlingViaExecution),
        suite_for_instruction_documentation(sut.setup('instruction name').description),
    ])


def _configuration_builder_with_exception_throwing_act_phase_setup() -> ConfigurationBuilder:
    return ConfigurationBuilder(pathlib.Path(),
                                ActPhaseHandling(_ActSourceAndExecutorConstructorThatRaisesException()))


class _ActSourceAndExecutorConstructorThatRaisesException(ActSourceAndExecutorConstructor):
    def apply(self, environment: InstructionEnvironmentForPreSdsStep, act_phase_instructions: list):
        raise ValueError('the method should never be called')


if __name__ == '__main__':
    unittest.main()
