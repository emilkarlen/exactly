import unittest

from .formatting_test_impls import list_of_paragraph_items
from .formatting_test_impls import lists
from .formatting_test_impls import literal_layout
from .formatting_test_impls import paragraph
from .formatting_test_impls import table


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(paragraph.suite())
    ret_val.addTest(lists.suite())
    ret_val.addTest(literal_layout.suite())
    ret_val.addTest(list_of_paragraph_items.suite())
    ret_val.addTest(table.suite())
    return ret_val


if __name__ == '__main__':
    unittest.main()
