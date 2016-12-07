import unittest

from exactly_lib_test.act_phase_setups import command_line, source_interpreter, shell_command_source_interpreter
from exactly_lib_test.act_phase_setups.command_line import executable_program_file
from exactly_lib_test.act_phase_setups.util import executor_made_of_parts


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(executor_made_of_parts.suite())
    ret_val.addTest(source_interpreter.suite())
    ret_val.addTest(command_line.suite())
    ret_val.addTest(shell_command_source_interpreter.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
