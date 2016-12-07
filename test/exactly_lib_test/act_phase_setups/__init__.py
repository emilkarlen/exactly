import unittest

from exactly_lib_test.act_phase_setups import command_line, interpreter, util
from exactly_lib_test.act_phase_setups.util import executor_made_of_parts


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(executor_made_of_parts.suite())
    ret_val.addTest(command_line.suite())
    ret_val.addTest(interpreter.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
