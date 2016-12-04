import unittest

from exactly_lib_test.help.suite_reporters import suite_reporter_documentations, render


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        render.suite(),
        suite_reporter_documentations.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
