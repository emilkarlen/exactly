import unittest

from exactly_lib_test.instructions.assert_.utils.expression import integer_resolver, instruction


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        integer_resolver.suite(),
        instruction.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
