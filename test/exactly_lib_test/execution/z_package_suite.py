import unittest

from exactly_lib_test.execution import phase_file_space
from exactly_lib_test.execution.full_execution import z_package_suite as full_execution
from exactly_lib_test.execution.impl import z_package_suite as impl
from exactly_lib_test.execution.partial_execution import z_package_suite as partial_execution


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(phase_file_space.suite())
    ret_val.addTest(impl.suite())
    ret_val.addTest(partial_execution.suite())
    ret_val.addTest(full_execution.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
