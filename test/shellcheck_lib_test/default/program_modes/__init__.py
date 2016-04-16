import unittest

from shellcheck_lib_test.default.program_modes import html_doc, help


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(help.suite())
    ret_val.addTest(html_doc.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
