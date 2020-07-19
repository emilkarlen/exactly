import unittest

from exactly_lib_test.test_case_utils.string_transformers.run_program import validation, unable_to_execute, arguments, \
    stdin, \
    transformation, environment, exit_code


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        validation.suite(),
        unable_to_execute.suite(),
        arguments.suite(),
        environment.suite(),
        stdin.suite(),
        transformation.suite(),
        exit_code.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
