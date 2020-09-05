import unittest

from exactly_lib_test.util.str_ import name, sequences, english_text


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        name.suite(),
        sequences.suite(),
        english_text.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
