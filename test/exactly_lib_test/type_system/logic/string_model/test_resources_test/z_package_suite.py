import unittest

from exactly_lib_test.type_system.logic.string_model.test_resources_test import string_models


def suite() -> unittest.TestSuite:
    return string_models.suite()


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
