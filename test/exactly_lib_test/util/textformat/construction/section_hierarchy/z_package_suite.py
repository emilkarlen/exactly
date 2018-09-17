import unittest

from exactly_lib_test.util.textformat.construction.section_hierarchy import table_of_contents, \
    hierarchies


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        table_of_contents.suite(),
        hierarchies.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
