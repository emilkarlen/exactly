import unittest

from shellcheck_lib_test.util.textformat.formatting.formatting_test_impls.table import \
    main, column_max_width, width_distribution


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(main.suite())
    ret_val.addTest(column_max_width.suite())
    ret_val.addTest(width_distribution.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
