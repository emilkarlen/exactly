import unittest

from exactly_lib_test.impls.instructions.assert_.process_output.exit_code import z_package_suite as exit_code
from exactly_lib_test.impls.instructions.assert_.process_output.stdout_err import z_package_suite as std_out_err


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        exit_code.suite(),
        std_out_err.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
