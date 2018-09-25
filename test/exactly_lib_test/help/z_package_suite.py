import unittest

from exactly_lib_test.help.entities import z_package_suite as entities
from exactly_lib_test.help.html_doc import z_package_suite as html_doc
from exactly_lib_test.help.program_modes import z_package_suite as program_modes
from exactly_lib_test.help.render import z_package_suite as render


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(render.suite())
    ret_val.addTest(program_modes.suite())
    ret_val.addTest(entities.suite())
    ret_val.addTest(html_doc.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
