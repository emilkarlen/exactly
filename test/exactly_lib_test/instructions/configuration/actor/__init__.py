import unittest

from exactly_lib.instructions.configuration import actor as sut
from exactly_lib_test.instructions.configuration.actor import failing_parse, executable_file, shell_command
from exactly_lib_test.instructions.test_resources.check_documentation import suite_for_instruction_documentation


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        failing_parse.suite(),
        executable_file.suite(),
        shell_command.suite(),
        suite_for_instruction_documentation(sut.setup('instruction name').documentation),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
