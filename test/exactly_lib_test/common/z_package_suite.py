import unittest

from exactly_lib_test.common import instruction_name_and_argument_splitter as splitter
from exactly_lib_test.common import result_reporting
from exactly_lib_test.common.err_msg import z_package_suite as err_msg
from exactly_lib_test.common.help import z_package_suite as help
from exactly_lib_test.common.report_rendering import z_package_suite as report_rendering


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        splitter.suite(),
        report_rendering.suite(),
        err_msg.suite(),
        result_reporting.suite(),
        help.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
