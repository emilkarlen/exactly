import unittest

from exactly_lib.default.program_modes.test_suite import CONFIGURATION_SECTION_INSTRUCTIONS
from exactly_lib.help.html_doc.parts import test_suite as sut
from exactly_lib.help.the_application_help import test_suite_help
from exactly_lib_test.help.test_resources.section_generator import generator_generates_valid_data


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def runTest(self):
        setup = test_suite_help(CONFIGURATION_SECTION_INSTRUCTIONS)
        generator = sut.generator('header', setup)
        generator_generates_valid_data(self, generator)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
