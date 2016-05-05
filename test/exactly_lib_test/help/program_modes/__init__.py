import unittest

from exactly_lib_test.help.program_modes import common, test_case, test_suite, help, html_doc


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(common.suite())
    ret_val.addTest(test_case.suite())
    ret_val.addTest(test_suite.suite())
    ret_val.addTest(help.suite())
    ret_val.addTest(html_doc.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
