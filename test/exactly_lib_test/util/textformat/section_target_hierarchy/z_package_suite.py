import unittest

from exactly_lib_test.util.textformat.section_target_hierarchy import hierarchies
from exactly_lib_test.util.textformat.section_target_hierarchy import table_of_contents


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        table_of_contents.suite(),
        hierarchies.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
