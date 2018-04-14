import unittest

from exactly_lib_test.util import functional, textformat, tables, \
    cli_syntax, symbol_table, collection
from exactly_lib_test.util import test_resources_test, process_execution


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(functional.suite())
    ret_val.addTest(symbol_table.suite())
    ret_val.addTest(test_resources_test.suite())  # These tests depend on symbol_table
    ret_val.addTest(tables.suite())
    ret_val.addTest(textformat.suite())
    ret_val.addTest(cli_syntax.suite())
    ret_val.addTest(collection.suite())
    ret_val.addTest(process_execution.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
