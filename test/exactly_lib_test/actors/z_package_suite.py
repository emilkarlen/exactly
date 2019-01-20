import unittest

from exactly_lib_test.actors import null
from exactly_lib_test.actors.command_line import z_package_suite as command_line
from exactly_lib_test.actors.file_interpreter import z_package_suite as file_interpreter
from exactly_lib_test.actors.source_interpreter import z_package_suite as source_interpreter
from exactly_lib_test.actors.util import z_package_suite as util


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(util.suite())
    ret_val.addTest(null.suite())
    ret_val.addTest(command_line.suite())
    ret_val.addTest(file_interpreter.suite())
    ret_val.addTest(source_interpreter.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
