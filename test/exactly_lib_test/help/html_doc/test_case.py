import unittest

from exactly_lib.help.entities.directives.entity_configuration import DIRECTIVE_ENTITY_CONFIGURATION
from exactly_lib.help.html_doc.parts import test_case as sut
from exactly_lib_test.help.program_modes.test_case.test_resources import test_case_help_with_production_phases
from exactly_lib_test.util.textformat.section_target_hierarchy.test_resources.generator_check import \
    generator_generates_valid_data


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def runTest(self):
        generator = sut.hierarchy('header',
                                  test_case_help_with_production_phases(),
                                  DIRECTIVE_ENTITY_CONFIGURATION)
        generator_generates_valid_data(self, generator)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
