import unittest

from exactly_lib_test.section_document import parse, test_syntax, parser_implementations, \
    new_parse_source, new_parser_classes


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(parse.suite())
    ret_val.addTest(test_syntax.suite())
    ret_val.addTest(new_parse_source.suite())
    ret_val.addTest(new_parser_classes.suite())
    ret_val.addTest(parser_implementations.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
