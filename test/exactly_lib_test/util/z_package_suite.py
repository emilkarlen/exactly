import unittest

from exactly_lib_test.util import functional, either, tables, \
    symbol_table, collection, value_lookup, file_utils
from exactly_lib_test.util.cli_syntax import z_package_suite as cli_syntax
from exactly_lib_test.util.description_tree import z_package_suite as description_tree
from exactly_lib_test.util.file_utils import z_package_suite as file_utils
from exactly_lib_test.util.interval import z_package_suite as interval
from exactly_lib_test.util.process_execution import z_package_suite as process_execution
from exactly_lib_test.util.render import z_package_suite as render
from exactly_lib_test.util.simple_textstruct import z_package_suite as simple_textstruct
from exactly_lib_test.util.str_ import z_package_suite as str_
from exactly_lib_test.util.test_resources_test import z_package_suite as test_resources_test
from exactly_lib_test.util.textformat import z_package_suite as textformat


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        value_lookup.suite(),
        functional.suite(),
        either.suite(),
        str_.suite(),
        symbol_table.suite(),
        test_resources_test.suite(),  # These tests depend on symbol_table,
        interval.suite(),
        tables.suite(),
        render.suite(),
        simple_textstruct.suite(),
        description_tree.suite(),
        textformat.suite(),
        cli_syntax.suite(),
        collection.suite(),
        process_execution.suite(),
        file_utils.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
