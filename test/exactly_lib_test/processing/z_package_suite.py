import unittest

from exactly_lib_test.processing import preprocessor
from exactly_lib_test.processing import processing_utils, processors
from exactly_lib_test.processing.parse import z_package_suite as parse
from exactly_lib_test.processing.standalone import z_package_suite as standalone
from exactly_lib_test.processing.test_resources_test import z_package_suite as test_resources_test


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources_test.suite(),
        preprocessor.suite(),
        processing_utils.suite(),
        parse.suite(),
        processors.suite(),
        standalone.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
