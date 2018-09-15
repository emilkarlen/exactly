import unittest

from exactly_lib_test.common import help, err_msg, result_reporting
from exactly_lib_test.common import instruction_name_and_argument_splitter as splitter


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        splitter.suite(),
        err_msg.suite(),
        result_reporting.suite(),
        help.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
