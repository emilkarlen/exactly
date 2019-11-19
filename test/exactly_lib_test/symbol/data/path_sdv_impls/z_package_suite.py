import unittest

from exactly_lib_test.symbol.data.path_sdv_impls import \
    path_part_sdvs, constant, path_with_symbol


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(path_part_sdvs.suite())
    ret_val.addTest(constant.suite())
    ret_val.addTest(path_with_symbol.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
