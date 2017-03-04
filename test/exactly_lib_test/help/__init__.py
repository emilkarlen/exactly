import unittest

from exactly_lib_test.help import program_modes, concepts, cross_reference_id, actors, suite_reporters, html_doc
from exactly_lib_test.help.utils import table_of_contents, section_hierarchy_rendering


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(cross_reference_id.suite())
    ret_val.addTest(table_of_contents.suite())
    ret_val.addTest(program_modes.suite())
    ret_val.addTest(section_hierarchy_rendering.suite())
    ret_val.addTest(concepts.suite())
    ret_val.addTest(actors.suite())
    ret_val.addTest(suite_reporters.suite())
    ret_val.addTest(html_doc.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
