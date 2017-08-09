import unittest

from exactly_lib_test.help_texts import cross_reference_id


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(cross_reference_id.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
