import unittest

from exactly_lib_test.instructions.assert_.utils.file_contents import contents_checkers, parts


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        contents_checkers.suite(),
        parts.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
