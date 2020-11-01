import unittest

from exactly_lib_test.type_val_deps.types.data import data_type_sdv_visitor


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(data_type_sdv_visitor.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
