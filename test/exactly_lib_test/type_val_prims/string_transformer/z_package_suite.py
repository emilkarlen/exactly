import unittest

from exactly_lib_test.type_val_prims.string_transformer import identity


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        identity.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
