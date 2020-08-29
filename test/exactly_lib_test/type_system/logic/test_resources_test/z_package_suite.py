import unittest

from exactly_lib_test.type_system.logic.test_resources_test import command_assertions
from exactly_lib_test.type_system.logic.test_resources_test import program_assertions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        command_assertions.suite(),
        program_assertions.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
