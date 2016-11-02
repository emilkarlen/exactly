import unittest

from exactly_lib_test.act_phase_setups import script_language_setup, single_command_setup, shell_command
from exactly_lib_test.act_phase_setups.util import executor_made_of_parts


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(executor_made_of_parts.suite())
    ret_val.addTest(script_language_setup.suite())
    ret_val.addTest(single_command_setup.suite())
    ret_val.addTest(shell_command.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
