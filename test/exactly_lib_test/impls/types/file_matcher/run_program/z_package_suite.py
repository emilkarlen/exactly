import unittest

from exactly_lib_test.impls.types.file_matcher.run_program import exit_code, arguments, environment, stdin, \
    validation, hard_error


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        validation.suite(),
        hard_error.suite(),
        exit_code.suite(),
        arguments.suite(),
        environment.suite(),
        stdin.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
