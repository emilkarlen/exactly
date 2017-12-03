import unittest

from exactly_lib.help.entities.suite_reporters import render as sut
from exactly_lib.help.entities.suite_reporters.entity_configuration import SUITE_REPORTER_ENTITY_CONFIGURATION
from exactly_lib.util.textformat.construction.section_contents_constructor import ConstructionEnvironment
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib_test.help.entities.suite_reporters.test_resources.documentation import SuiteReporterDocTestImpl
from exactly_lib_test.util.textformat.construction.section_hierarchy.test_resources.misc import \
    CrossReferenceTextConstructorTestImpl
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestIndividualSuiteReporter),
        unittest.makeSuite(TestAllSuiteReportersList),
    ])


class TestAllSuiteReportersList(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        constructor = SUITE_REPORTER_ENTITY_CONFIGURATION.cli_list_constructor_getter.get_constructor(
            [SuiteReporterDocTestImpl('reporter 1'),
             SuiteReporterDocTestImpl('reporter 2')])
        # ACT #
        actual = constructor.apply(CONSTRUCTION_ENVIRONMENT)
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
                constructor = sut.IndividualSuiteReporterConstructor(doc)
                # ACT #
                actual = constructor.apply(CONSTRUCTION_ENVIRONMENT)
                # ASSERT #
                struct_check.is_article_contents.apply(self, actual)


CONSTRUCTION_ENVIRONMENT = ConstructionEnvironment(CrossReferenceTextConstructorTestImpl())

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
