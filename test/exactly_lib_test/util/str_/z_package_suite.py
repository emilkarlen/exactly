import unittest

from exactly_lib_test.util.str_ import name, english_text, read_lines, sequences


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        name.suite(),
        sequences.suite(),
        english_text.suite(),
        read_lines.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
