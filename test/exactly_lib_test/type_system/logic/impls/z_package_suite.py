import unittest

from exactly_lib_test.type_system.logic.impls import transformed_string_models


def suite() -> unittest.TestSuite:
    return transformed_string_models.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
