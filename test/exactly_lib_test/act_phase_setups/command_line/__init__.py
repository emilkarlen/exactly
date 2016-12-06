import unittest

from exactly_lib_test.act_phase_setups.command_line import executable_program_file, shell_command


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(executable_program_file.suite())
    ret_val.addTest(shell_command.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
