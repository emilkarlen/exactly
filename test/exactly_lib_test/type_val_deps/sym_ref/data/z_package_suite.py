import unittest

from exactly_lib_test.type_val_deps.sym_ref.data import reference_restrictions


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(reference_restrictions.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
