import unittest

from exactly_lib_test.cli.program_modes.help.program_modes import test_case


def suite() -> unittest.TestSuite:
    return test_case.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
