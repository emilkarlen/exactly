import unittest

from exactly_lib_test.test_case_utils.string_transformers.run_program import validation, hard_error, arguments, stdin, \
    transformation, environment


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        validation.suite(),
        hard_error.suite(),
        arguments.suite(),
        environment.suite(),
        stdin.suite(),
        transformation.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
