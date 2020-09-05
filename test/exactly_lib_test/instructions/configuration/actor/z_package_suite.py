import unittest

from exactly_lib.instructions.configuration import actor as sut
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.instructions.configuration.actor import failing_parse, command_line, file_interpreter, \
    source_interpreter, null


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        failing_parse.suite(),
        null.suite(),
        command_line.suite(),
        file_interpreter.suite(),
        source_interpreter.suite(),
        suite_for_instruction_documentation(sut.setup('instruction name').documentation),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
