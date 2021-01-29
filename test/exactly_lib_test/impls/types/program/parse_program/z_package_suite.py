import unittest

from exactly_lib_test.impls.types.program.parse_program import invalid_syntax, \
    arguments, \
    all_forms_wo_optional_components, all_forms_w_optional_components, \
    stdin, transformation, within_parens


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        invalid_syntax.suite(),
        all_forms_wo_optional_components.suite(),
        arguments.suite(),
        stdin.suite(),
        transformation.suite(),
        all_forms_w_optional_components.suite(),
        within_parens.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
