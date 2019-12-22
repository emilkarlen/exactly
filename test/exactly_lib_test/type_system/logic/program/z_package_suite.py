import unittest

from exactly_lib_test.type_system.logic.program import commands


def suite() -> unittest.TestSuite:
    return commands.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
