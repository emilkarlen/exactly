import unittest

from exactly_lib.help.actors.entity_configuration import ACTOR_ENTITY_CONFIGURATION
from exactly_lib.help.html_doc.parts import test_case as sut
from exactly_lib.help.types.entity_configuration import TYPE_ENTITY_CONFIGURATION
from exactly_lib_test.help.program_modes.test_case.test_resources import test_case_help_with_production_phases
from exactly_lib_test.help.test_resources.section_generator import generator_generates_valid_data


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def runTest(self):
        generator = sut.generator('header',
                                  test_case_help_with_production_phases(),
                                  ACTOR_ENTITY_CONFIGURATION,
                                  TYPE_ENTITY_CONFIGURATION)
        generator_generates_valid_data(self, generator)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
