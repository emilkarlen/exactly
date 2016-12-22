import unittest

from exactly_lib.instructions.configuration import actor as sut
from exactly_lib.instructions.configuration.utils import actor_utils
from exactly_lib_test.act_phase_setups.command_line.test_resources import shell_command_source_line_for
from exactly_lib_test.instructions.configuration.actor import failing_parse, executable_file, shell_command
from exactly_lib_test.instructions.configuration.actor.test_resources import Arrangement, Expectation, _check
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.test_resources.programs import shell_commands
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as pr
from exactly_lib_test.test_resources.value_assertions import value_assertion as va


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        failing_parse.suite(),
        executable_file.suite(),
        shell_command.suite(),
        unittest.makeSuite(TestShellHandlingViaExecution),
        suite_for_instruction_documentation(sut.setup('instruction name').documentation),
    ])


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
