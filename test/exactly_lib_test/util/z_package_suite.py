import unittest

from exactly_lib_test.util import functional, tables, \
    symbol_table, collection
from exactly_lib_test.util.cli_syntax import z_package_suite as cli_syntax
from exactly_lib_test.util.process_execution import z_package_suite as process_execution
from exactly_lib_test.util.test_resources_test import z_package_suite as test_resources_test
from exactly_lib_test.util.textformat import z_package_suite as textformat


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
