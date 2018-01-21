import unittest

from exactly_lib_test.processing import parse
from exactly_lib_test.processing import preprocessor
from exactly_lib_test.processing import processing_utils, processors


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        preprocessor.suite(),
        processing_utils.suite(),
        parse.suite(),
        processors.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
