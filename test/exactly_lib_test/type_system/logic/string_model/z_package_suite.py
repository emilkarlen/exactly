import unittest

from exactly_lib_test.type_system.logic.string_model import from_lines


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        from_lines.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
