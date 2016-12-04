import unittest

from exactly_lib.help.suite_reporters import render as sut
from exactly_lib.help.utils.render import RenderingEnvironment
from exactly_lib_test.help.suite_reporters.test_resources.documentation import SuiteReporterDocTestImpl
from exactly_lib_test.help.test_resources import CrossReferenceTextConstructorTestImpl
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestIndividualSuiteReporter),
        unittest.makeSuite(TestAllSuiteReportersList),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())


class TestAllSuiteReportersList(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        renderer = sut.all_suite_reporters_list_renderer([SuiteReporterDocTestImpl('reporter 1'),
                                                          SuiteReporterDocTestImpl('reporter 2')])
        # ACT #
        actual = renderer.apply(RENDERING_ENVIRONMENT)
        # ASSERT #
        struct_check.is_section_contents.apply(self, actual)


class TestIndividualSuiteReporter(unittest.TestCase):
    def test_render(self):
        # ARRANGE #
        doc = SuiteReporterDocTestImpl('name')
        renderer = sut.IndividualSuiteReporterRenderer(doc)
        # ACT #
        actual = renderer.apply(RENDERING_ENVIRONMENT)
        # ASSERT #
        struct_check.is_section_contents.apply(self, actual)


RENDERING_ENVIRONMENT = RenderingEnvironment(CrossReferenceTextConstructorTestImpl())
