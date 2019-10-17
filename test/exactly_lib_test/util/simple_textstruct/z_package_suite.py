import unittest

from exactly_lib_test.util.simple_textstruct import structure
from exactly_lib_test.util.simple_textstruct.file_printer_output import z_package_suite as file_printer_output
from exactly_lib_test.util.simple_textstruct.rendering import z_package_suite as rendering
from exactly_lib_test.util.simple_textstruct.test_resources_test import z_package_suite as test_resources_test


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        structure.suite(),
        test_resources_test.suite(),
        rendering.suite(),
        file_printer_output.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
