import unittest

from exactly_lib_test.type_system.logic.test_resources_test import program_assertions


def suite() -> unittest.TestSuite:
    return program_assertions.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
