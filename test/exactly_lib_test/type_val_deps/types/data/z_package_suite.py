import unittest

from exactly_lib_test.type_val_deps.types.data import data_type_sdv_visitor
from exactly_lib_test.type_val_deps.types.data import value_restrictions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        data_type_sdv_visitor.suite(),
        value_restrictions.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
