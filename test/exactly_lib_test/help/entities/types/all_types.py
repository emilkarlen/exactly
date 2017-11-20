import unittest

from exactly_lib.help.entities.types.all_types import all_types
from exactly_lib_test.help.entities.types.test_resources import \
    suite_for_single_documentation


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        suite_for_single_documentation(doc)
        for doc in all_types()
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
