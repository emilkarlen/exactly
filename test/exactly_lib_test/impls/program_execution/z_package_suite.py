import unittest

from exactly_lib_test.impls.program_execution import execution


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        execution.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
