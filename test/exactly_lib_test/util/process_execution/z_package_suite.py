import unittest

from exactly_lib_test.util.process_execution import store_result_in_files


def suite() -> unittest.TestSuite:
    return store_result_in_files.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
