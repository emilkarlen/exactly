import unittest

from exactly_lib_test.util.textformat.rendering.html import z_package_suite as html
from exactly_lib_test.util.textformat.rendering.text import z_package_suite as text


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        text.suite(),
        html.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
