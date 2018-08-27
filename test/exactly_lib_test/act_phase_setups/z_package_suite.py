import unittest

from exactly_lib_test.act_phase_setups import null, command_line, source_interpreter, file_interpreter
from exactly_lib_test.act_phase_setups.util import executor_made_of_parts


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(executor_made_of_parts.suite())
    ret_val.addTest(null.suite())
    ret_val.addTest(command_line.suite())
    ret_val.addTest(file_interpreter.suite())
    ret_val.addTest(source_interpreter.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
