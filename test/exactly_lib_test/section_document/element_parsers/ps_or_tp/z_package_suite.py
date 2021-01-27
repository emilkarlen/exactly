import unittest

from exactly_lib_test.section_document.element_parsers.ps_or_tp import parser_opt_parens


def suite() -> unittest.TestSuite:
    return parser_opt_parens.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
