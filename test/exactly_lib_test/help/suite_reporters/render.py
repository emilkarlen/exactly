import unittest

from exactly_lib.help.suite_reporters import render as sut
from exactly_lib.help.utils.section_contents_renderer import RenderingEnvironment
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
        paragraphs = docs.paras('simple paragraph')
        document_variants = [
            SuiteReporterDocTestImpl('as little content as possible'),
            SuiteReporterDocTestImpl('with main_description_rest',
                                     main_description_rest=paragraphs),
            SuiteReporterDocTestImpl('with syntax_of_output',
                                     syntax_of_output=paragraphs),
            SuiteReporterDocTestImpl('with exit_code_description',
                                     exit_code_description=paragraphs),
            SuiteReporterDocTestImpl('with syntax_of_output and exit_code_description',
                                     syntax_of_output=paragraphs,
                                     exit_code_description=paragraphs),
            SuiteReporterDocTestImpl('with everything',
                                     main_description_rest=paragraphs,
                                     syntax_of_output=paragraphs,
                                     exit_code_description=paragraphs),
        ]
        for doc in document_variants:
            with self.subTest(doc_name=doc.singular_name()):
                renderer = sut.IndividualSuiteReporterRenderer(doc)
                # ACT #
                actual = renderer.apply(RENDERING_ENVIRONMENT)
                # ASSERT #
                struct_check.is_section_contents.apply(self, actual)


RENDERING_ENVIRONMENT = RenderingEnvironment(CrossReferenceTextConstructorTestImpl())
