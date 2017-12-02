import unittest

from exactly_lib_test.help import program_modes, html_doc, entities
from exactly_lib_test.help.utils import section_hierarchy_rendering
from exactly_lib_test.util.textformat.construction.section_hierarchy import table_of_contents


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(table_of_contents.suite())
    ret_val.addTest(program_modes.suite())
    ret_val.addTest(section_hierarchy_rendering.suite())
    ret_val.addTest(entities.suite())
    ret_val.addTest(html_doc.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
