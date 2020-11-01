import unittest

from exactly_lib_test.type_val_deps.sym_ref.test_resources_test import concrete_restriction_assertion
from exactly_lib_test.type_val_deps.sym_ref.test_resources_test import container_assertions
from exactly_lib_test.type_val_deps.sym_ref.test_resources_test import restrictions_assertions
from exactly_lib_test.type_val_deps.sym_ref.test_resources_test import sdv_assertions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        restrictions_assertions.suite(),
        sdv_assertions.suite(),
        container_assertions.suite(),
        concrete_restriction_assertion.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
