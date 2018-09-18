import unittest

from exactly_lib_test.help import program_modes, html_doc, entities, file_inclusion_directive
from exactly_lib_test.help.render import z_package_suite as render


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(render.suite())
    ret_val.addTest(program_modes.suite())
    ret_val.addTest(file_inclusion_directive.suite())
    ret_val.addTest(entities.suite())
    ret_val.addTest(html_doc.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
