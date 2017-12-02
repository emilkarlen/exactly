import unittest

from exactly_lib_test.util.textformat.rendering.text.formatting_test_impls.table import \
    column_max_width, width_distribution
from exactly_lib_test.util.textformat.rendering.text.formatting_test_impls.table import main


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(main.suite())
    ret_val.addTest(column_max_width.suite())
    ret_val.addTest(width_distribution.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
