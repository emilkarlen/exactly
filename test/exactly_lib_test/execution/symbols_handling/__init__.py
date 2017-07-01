import unittest

from exactly_lib_test.execution.symbols_handling import restriction_failure_renderer, symbol_validation


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(restriction_failure_renderer.suite())
    ret_val.addTest(symbol_validation.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
