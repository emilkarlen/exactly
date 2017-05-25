import unittest

from exactly_lib_test.instructions.multi_phase_instructions.utils import parse


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        parse.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
