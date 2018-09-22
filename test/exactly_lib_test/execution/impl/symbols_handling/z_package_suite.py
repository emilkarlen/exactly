import unittest

from exactly_lib_test.execution.impl.symbols_handling import restriction_failure_renderer
from exactly_lib_test.execution.impl.symbols_handling import symbol_validation


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        restriction_failure_renderer.suite(),
        symbol_validation.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
