import unittest

from exactly_lib.help.html_doc.parts import test_case as sut
from exactly_lib_test.help.program_modes.test_case.test_resources import TEST_CASE_HELP_WITH_PRODUCTION_PHASES
from exactly_lib_test.help.test_resources.section_generator import generator_generates_valid_data


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def runTest(self):
        generator = sut.generator('header', TEST_CASE_HELP_WITH_PRODUCTION_PHASES)
        generator_generates_valid_data(self, generator)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
