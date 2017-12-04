import unittest

from exactly_lib_test.instructions.assert_.utils.condition.integer import integer_resolver


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        integer_resolver.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
