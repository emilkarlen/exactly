import unittest

from exactly_lib_test.type_system.logic.lines_transformer import identity


def suite() -> unittest.TestSuite:
    return identity.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
