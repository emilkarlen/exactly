import unittest

from exactly_lib_test.util.textformat import formatting, structure, parse, utils


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(formatting.suite())
    ret_val.addTest(structure.suite())
    ret_val.addTest(parse.suite())
    ret_val.addTest(utils.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
