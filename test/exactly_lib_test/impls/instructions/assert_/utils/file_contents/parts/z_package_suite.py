import unittest

from exactly_lib_test.impls.instructions.assert_.utils.file_contents.parts import line_matches


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        line_matches.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
