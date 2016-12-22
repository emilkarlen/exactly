import unittest

from exactly_lib.instructions.configuration import actor as sut
from exactly_lib.instructions.configuration.utils import actor_utils
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib_test.act_phase_setups.command_line.test_resources import shell_command_source_line_for
from exactly_lib_test.instructions.configuration.actor import executable_file, shell_command
from exactly_lib_test.instructions.configuration.actor.test_resources import Arrangement, Expectation, _check
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.test_resources.parse import new_source2
from exactly_lib_test.test_resources.programs import shell_commands
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as pr
from exactly_lib_test.test_resources.value_assertions import value_assertion as va


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFailingParseForAnyActor),
        unittest.makeSuite(TestFailingParseForCommandLineActor),
        unittest.makeSuite(TestFailingParseForSourceInterpreterActor),
        executable_file.suite(),
        shell_command.suite(),
        unittest.makeSuite(TestShellHandlingViaExecution),
        suite_for_instruction_documentation(sut.setup('instruction name').documentation),
    ])


class TestFailingParseForAnyActor(unittest.TestCase):
    def test_fail_when_there_is_no_arguments(self):
        source = new_source2('   ')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().apply(source)

    def test_fail_when_the_quoting_is_invalid(self):
        source = new_source2('argument-1 "argument-2')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().apply(source)


class TestFailingParseForCommandLineActor(unittest.TestCase):
    def test_fail_when_extra_unexpected_argument(self):
        source = new_source2(actor_utils.COMMAND_LINE_ACTOR_OPTION + ' extra-unexpected-argument')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().apply(source)


class TestFailingParseForSourceInterpreterActor(unittest.TestCase):
    def test_fail_when_missing_program_argument(self):
        source = new_source2(actor_utils.SOURCE_INTERPRETER_OPTION)
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().apply(source)


class TestShellHandlingViaExecution(unittest.TestCase):
    def test_valid_shell_command(self):
        act_phase_source_line = shell_command_source_line_for(
            shell_commands.command_that_prints_line_to_stdout('output on stdout'))
        _check(self,
               Arrangement(actor_utils.COMMAND_LINE_ACTOR_OPTION,
                           [act_phase_source_line]),
               Expectation(sub_process_result_from_execute=pr.stdout(va.Equals('output on stdout\n',
                                                                               'expected output on stdout')))
               )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
