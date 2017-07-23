import unittest

from exactly_lib.instructions.configuration.utils.actor_utils import COMMAND_LINE_ACTOR_OPTION
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_suite.instruction_set.sections.configuration import actor as sut
from exactly_lib.test_suite.instruction_set.sections.configuration.instruction_definition import \
    ConfigurationSectionInstruction
from exactly_lib_test.act_phase_setups.command_line.test_resources import shell_command_source_line_for
from exactly_lib_test.act_phase_setups.test_resources import act_phase_execution
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_case.test_resources.act_phase_os_process_executor import \
    ActPhaseOsProcessExecutorThatRecordsArguments
from exactly_lib_test.test_resources.parse import remaining_source
from exactly_lib_test.test_suite.instruction_set.sections.configuration.test_resources import \
    configuration_section_environment


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParse),
        unittest.makeSuite(TestSuccessfulParseAndInstructionExecutionForShellCommandActor),
        suite_for_instruction_documentation(sut.actor_utils.InstructionDocumentation('instruction mame',
                                                                                     'single line description',
                                                                                     'description-rest')),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())


class TestParse(unittest.TestCase):
    def test_fail_when_invalid_syntax(self):
        test_cases = [
            '   ',
            'argument-1 "argument-2',
        ]
        parser = sut.Parser()
        for instruction_argument in test_cases:
            with self.subTest(msg='instruction argument=' + repr(instruction_argument)):
                for source in equivalent_source_variants__with_source_check(self, instruction_argument):
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        parser.parse(source)

    def test_success_when_argument_is_valid(self):
        parser = sut.Parser()
        for source in equivalent_source_variants__with_source_check(self, COMMAND_LINE_ACTOR_OPTION):
            parser.parse(source)


class TestSuccessfulParseAndInstructionExecutionForShellCommandActor(unittest.TestCase):
    """
    Not a beautiful test.
    This test mimics the test of the actor instruction of the test-case/configuration phase.

    This test should probably be refactored. But not clear what is the best way to do it, at the moment.
    """

    def test_act_phase_source_is_single_shell_command(self):
        # ARRANGE #
        os_process_executor = ActPhaseOsProcessExecutorThatRecordsArguments()
        source = remaining_source(COMMAND_LINE_ACTOR_OPTION)
        instruction = sut.Parser().parse(source)
        assert isinstance(instruction, ConfigurationSectionInstruction)
        environment = configuration_section_environment()
        # ACT #
        instruction.execute(environment)
        executor_constructor = environment.act_phase_setup.source_and_executor_constructor
        act_phase_instructions = [instr([shell_command_source_line_for('act phase source line')])]
        act_phase_execution.check_execution(self,
                                            executor_constructor,
                                            act_phase_execution.Arrangement(
                                                act_phase_instructions=act_phase_instructions,
                                                act_phase_process_executor=os_process_executor),
                                            act_phase_execution.Expectation())
        # ASSERT #
        self.assertTrue(os_process_executor.command.shell,
                        'Command should indicate shell execution')
        actual_cmd_and_args = os_process_executor.command.args
        self.assertIsInstance(actual_cmd_and_args, str,
                              'Arguments of command to execute should be a string')
        self.assertEqual(actual_cmd_and_args,
                         'act phase source line')
