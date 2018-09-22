import unittest

from exactly_lib_test.instructions.assert_.utils.file_contents import contents_checkers
from exactly_lib_test.instructions.assert_.utils.file_contents.parts import z_package_suite as parts


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        contents_checkers.suite(),
        parts.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
