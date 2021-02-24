import unittest

from exactly_lib_test.type_val_deps.sym_ref.w_str_rend_restrictions import visitor, on_direct_and_indirect, \
    or_restriction, value_restrictions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        visitor.suite(),
        value_restrictions.suite(),
        on_direct_and_indirect.suite(),
        or_restriction.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
