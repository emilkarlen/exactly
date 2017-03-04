import unittest

from exactly_lib_test.help.html_doc.parts import test_case


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_case.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
