import unittest

from exactly_lib_test.instructions.assert_.utils.expression import instruction, integer


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        instruction.suite(),
        integer.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
