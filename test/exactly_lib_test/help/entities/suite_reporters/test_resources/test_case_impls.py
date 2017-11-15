import unittest

from exactly_lib.help.entities.suite_reporters.contents_structure import SuiteReporterDocumentation
from exactly_lib.help_texts.entity_identifiers import SUITE_REPORTER_ENTITY_TYPE_IDENTIFIER
from exactly_lib_test.common.help.test_resources import see_also_assertions as asrt_see_also
from exactly_lib_test.help_texts.test_resources import cross_reference_id_va as xref_va
from exactly_lib_test.test_resources.test_case_base_with_short_description import \
    TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


def suite_for_suite_reporter_documentation(documentation: SuiteReporterDocumentation) -> unittest.TestSuite:
    return unittest.TestSuite(tcc(documentation) for tcc in [
        TestName,
        TestSingleLineDescriptionStr,
        TestSingleLineDescription,
        TestNameAndSingleLineDescriptionStr,
        TestNameAndSingleLineDescription,
        TestMainDescriptionRest,
        TestSyntax,
        TestExitCodeDescription,
        TestSeeAlso,
        TestCrossReferenceTarget,
    ])


class WithSuiteReporterDocumentationBase(TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType):
    def __init__(self, documentation: SuiteReporterDocumentation):
        super().__init__(documentation)
        self.documentation = documentation


class TestName(WithSuiteReporterDocumentationBase):
    def runTest(self):
        actual = self.documentation.singular_name()
        self.assertIsInstance(actual, str, 'name')


class TestSingleLineDescriptionStr(WithSuiteReporterDocumentationBase):
    def runTest(self):
        actual = self.documentation.single_line_description_str()
        self.assertIsInstance(actual, str, 'single_line_description_str')


class TestSingleLineDescription(WithSuiteReporterDocumentationBase):
    def runTest(self):
        actual = self.documentation.single_line_description()
        struct_check.is_text.apply_with_message(self, actual, 'single_line_description')


class TestNameAndSingleLineDescriptionStr(WithSuiteReporterDocumentationBase):
    def runTest(self):
        actual = self.documentation.name_and_single_line_description_str()
        self.assertIsInstance(actual, str, 'name_and_single_line_description_str')


class TestNameAndSingleLineDescription(WithSuiteReporterDocumentationBase):
    def runTest(self):
        actual = self.documentation.name_and_single_line_description()
        struct_check.is_text.apply_with_message(self, actual, 'name_and_single_line_description')


class TestMainDescriptionRest(WithSuiteReporterDocumentationBase):
    def runTest(self):
        actual = self.documentation.main_description_rest()
        struct_check.is_paragraph_item_list().apply_with_message(self, actual,
                                                                 'main_description_rest')


class TestSyntax(WithSuiteReporterDocumentationBase):
    def runTest(self):
        actual = self.documentation.syntax_of_output()
        struct_check.is_paragraph_item_list().apply_with_message(self, actual,
                                                                 'syntax_of_output')


class TestExitCodeDescription(WithSuiteReporterDocumentationBase):
    def runTest(self):
        actual = self.documentation.exit_code_description()
        struct_check.is_paragraph_item_list().apply_with_message(self, actual,
                                                                 'main_description_rest')


class TestSeeAlso(WithSuiteReporterDocumentationBase):
    def runTest(self):
        actual = self.documentation.see_also_targets()
        asrt_see_also.is_see_also_target_list.apply_with_message(self, actual, 'see_also_targets')


class TestCrossReferenceTarget(WithSuiteReporterDocumentationBase):
    def runTest(self):
        actual = self.documentation.cross_reference_target()
        assertion = xref_va.is_entity_for_type(SUITE_REPORTER_ENTITY_TYPE_IDENTIFIER)
        assertion.apply_with_message(self, actual, 'cross_reference_target')
