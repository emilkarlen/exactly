import unittest

from exactly_lib_test.util import functional, textformat, tables, \
    cli_syntax, symbol_table, collection
from exactly_lib_test.util import test_resources_test
from exactly_lib_test.util.process_execution import package_test_suite as process_execution


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        functional.suite(),
        symbol_table.suite(),
        test_resources_test.suite(),  # These tests depend on symbol_table,
        tables.suite(),
        textformat.suite(),
        cli_syntax.suite(),
        collection.suite(),
        process_execution.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
