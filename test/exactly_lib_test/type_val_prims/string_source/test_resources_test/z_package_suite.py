import unittest

from exactly_lib_test.type_val_prims.string_source.test_resources_test import contents_assertions, assertions, \
    multi_obj_assertions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        contents_assertions.suite(),
        assertions.suite(),
        multi_obj_assertions.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
