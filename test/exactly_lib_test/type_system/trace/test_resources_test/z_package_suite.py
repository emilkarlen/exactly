import unittest

from exactly_lib_test.type_system.trace.test_resources_test import trace_assertions


def suite() -> unittest.TestSuite:
    return trace_assertions.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
