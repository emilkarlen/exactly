import unittest

from exactly_lib_test.type_val_deps.types.path.path_sdv_impls import constant, path_with_symbol
from exactly_lib_test.type_val_deps.types.path.path_sdv_impls import \
    path_part_sdvs


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(path_part_sdvs.suite())
    ret_val.addTest(constant.suite())
    ret_val.addTest(path_with_symbol.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
