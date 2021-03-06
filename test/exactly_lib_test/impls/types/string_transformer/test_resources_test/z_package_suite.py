import unittest

from exactly_lib_test.impls.types.string_transformer.test_resources_test import \
    test_transformers, integration_check


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_transformers.suite(),
        integration_check.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
