import unittest

from exactly_lib_test.act_phase_setups import source_interpreter, single_command_setup, shell_command, \
    shell_command_source_interpreter
from exactly_lib_test.act_phase_setups.util import executor_made_of_parts


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(executor_made_of_parts.suite())
    ret_val.addTest(source_interpreter.suite())
    ret_val.addTest(single_command_setup.suite())
    ret_val.addTest(shell_command.suite())
    ret_val.addTest(shell_command_source_interpreter.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
