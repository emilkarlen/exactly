import unittest

from exactly_lib_test.impls.types.string_transformer.run_program import validation, unable_to_execute, arguments, \
    stdin, \
    transformation, environment, exit_code, dep_on_ext_resources


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        validation.suite(),
        unable_to_execute.suite(),
        arguments.suite(),
        environment.suite(),
        stdin.suite(),
        transformation.suite(),
        exit_code.suite(),
        dep_on_ext_resources.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
