import unittest

from exactly_lib_test.util.textformat.formatting.text import wrapper
from . import lists
from . import paragraph_item
from . import section


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(wrapper.suite())
    ret_val.addTest(lists.suite())
    ret_val.addTest(paragraph_item.suite())
    ret_val.addTest(section.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
