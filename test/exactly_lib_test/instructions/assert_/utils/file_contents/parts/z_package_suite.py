import unittest

from exactly_lib_test.instructions.assert_.utils.file_contents.parts import file_assertion_part, line_matches


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        file_assertion_part.suite(),
        line_matches.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
