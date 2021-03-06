import unittest

from exactly_lib_test.util.textformat.rendering.text import lists, paragraph_item, section, wrapper


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(wrapper.suite())
    ret_val.addTest(lists.suite())
    ret_val.addTest(paragraph_item.suite())
    ret_val.addTest(section.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
