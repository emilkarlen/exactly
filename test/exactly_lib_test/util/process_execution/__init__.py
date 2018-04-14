import unittest

from exactly_lib_test.util.process_execution import sub_process_execution


def suite() -> unittest.TestSuite:
    return sub_process_execution.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
