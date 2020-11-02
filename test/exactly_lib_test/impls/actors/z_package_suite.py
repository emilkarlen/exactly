import unittest

from exactly_lib_test.impls.actors import null
from exactly_lib_test.impls.actors.file_interpreter import z_package_suite as file_interpreter
from exactly_lib_test.impls.actors.program import z_package_suite as program
from exactly_lib_test.impls.actors.source_interpreter import z_package_suite as source_interpreter
from exactly_lib_test.impls.actors.util import z_package_suite as util


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(util.suite())
    ret_val.addTest(null.suite())
    ret_val.addTest(program.suite())
    ret_val.addTest(file_interpreter.suite())
    ret_val.addTest(source_interpreter.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
