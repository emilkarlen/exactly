import unittest

from exactly_lib_test.help.entities.actors import z_package_suite as actors
from exactly_lib_test.help.entities.concepts import z_package_suite as concepts
from exactly_lib_test.help.entities.configuration_parameters import z_package_suite as configuration_parameters
from exactly_lib_test.help.entities.directives import z_package_suite as directives
from exactly_lib_test.help.entities.suite_reporters import z_package_suite as suite_reporters
from exactly_lib_test.help.entities.syntax_elements import z_package_suite as syntax_elements
from exactly_lib_test.help.entities.types import z_package_suite as types


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(directives.suite())
    ret_val.addTest(concepts.suite())
    ret_val.addTest(actors.suite())
    ret_val.addTest(suite_reporters.suite())
    ret_val.addTest(syntax_elements.suite())
    ret_val.addTest(configuration_parameters.suite())
    ret_val.addTest(types.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
