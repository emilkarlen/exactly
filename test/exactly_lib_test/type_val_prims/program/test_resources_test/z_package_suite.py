import unittest

from exactly_lib_test.type_val_prims.program.test_resources_test import command_assertions, program_assertions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        command_assertions.suite(),
        program_assertions.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
