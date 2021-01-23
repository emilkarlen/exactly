import unittest

from exactly_lib_test.impls.types.string_source.command_output import unable_to_execute, successful_output, \
    non_zero_exit_code


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        successful_output.suite(),
        non_zero_exit_code.suite(),
        unable_to_execute.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
