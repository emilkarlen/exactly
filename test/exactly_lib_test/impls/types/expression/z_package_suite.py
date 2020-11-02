import unittest

from exactly_lib_test.impls.types.expression import parse_wo_precedences, parse_w_precedences, syntax_documentation


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        syntax_documentation.suite(),
        parse_wo_precedences.suite(),
        parse_w_precedences.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
