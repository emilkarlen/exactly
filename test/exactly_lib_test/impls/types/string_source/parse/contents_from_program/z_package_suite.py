import unittest

from exactly_lib_test.impls.types.string_source.parse.contents_from_program import successful_output, \
    syntax_and_validation, non_zero_exit_code_or_unable_to_execute, stdin


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        syntax_and_validation.suite(),
        successful_output.suite(),
        non_zero_exit_code_or_unable_to_execute.suite(),
        stdin.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
