import unittest

from shellcheck_lib_test.util.textformat import formatting, parse, utils


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(formatting.suite())
    ret_val.addTest(parse.suite())
    ret_val.addTest(utils.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
