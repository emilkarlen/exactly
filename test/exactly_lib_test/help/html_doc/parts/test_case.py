import unittest

from exactly_lib.help.html_doc.parts import test_case as sut
from exactly_lib_test.help.program_modes.test_case.test_resources import test_case_help_with_production_phases
from exactly_lib_test.util.textformat.construction.section_hierarchy.test_resources.generator_check import \
    generator_generates_valid_data


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def runTest(self):
        generator = sut.generator('header',
                                  test_case_help_with_production_phases())
        generator_generates_valid_data(self, generator)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
