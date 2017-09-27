import unittest

from exactly_lib.help.syntax_elements.contents_structure import SyntaxElementDocumentation
from exactly_lib.help_texts.entity_names import SYNTAX_ELEMENT_ENTITY_TYPE_NAME
from exactly_lib_test.common.help.test_resources import see_also_assertions as asrt_see_also
from exactly_lib_test.common.help.test_resources.syntax_contents_structure_assertions import is_invokation_variant
from exactly_lib_test.help_texts.test_resources import cross_reference_id_va as xref_va
from exactly_lib_test.test_resources.test_case_base_with_short_description import \
    TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


def suite_for_syntax_element_documentation(documentation: SyntaxElementDocumentation) -> unittest.TestSuite:
    return unittest.TestSuite(tcc(documentation) for tcc in [
        TestCrossReferenceTarget,

        TestName,
        TestSingleLineDescriptionStr,
        TestSingleLineDescription,
        TestNameAndSingleLineDescriptionStr,
        TestNameAndSingleLineDescription,

        TestMainDescriptionRest,
        TestInvokationVariants,

        TestSeeAlso,
    ])


class WithSyntaxElementDocumentationBase(TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType):
    def __init__(self, documentation: SyntaxElementDocumentation):
        super().__init__(documentation)
        self.documentation = documentation


class TestCrossReferenceTarget(WithSyntaxElementDocumentationBase):
    def runTest(self):
        actual = self.documentation.cross_reference_target()
        assertion = xref_va.is_entity_for_type(SYNTAX_ELEMENT_ENTITY_TYPE_NAME)
        assertion.apply_with_message(self, actual, 'cross_reference_target')


class TestName(WithSyntaxElementDocumentationBase):
    def runTest(self):
        actual = self.documentation.singular_name()
        self.assertIsInstance(actual, str, 'name')


class TestSingleLineDescriptionStr(WithSyntaxElementDocumentationBase):
    def runTest(self):
        actual = self.documentation.single_line_description_str()
        self.assertIsInstance(actual, str, 'single_line_description_str')


class TestSingleLineDescription(WithSyntaxElementDocumentationBase):
    def runTest(self):
        actual = self.documentation.single_line_description()
        struct_check.is_text.apply_with_message(self, actual, 'single_line_description')


class TestNameAndSingleLineDescriptionStr(WithSyntaxElementDocumentationBase):
    def runTest(self):
        actual = self.documentation.name_and_single_line_description_str()
        self.assertIsInstance(actual, str, 'name_and_single_line_description_str')


class TestNameAndSingleLineDescription(WithSyntaxElementDocumentationBase):
    def runTest(self):
        actual = self.documentation.name_and_single_line_description()
        struct_check.is_text.apply_with_message(self, actual, 'name_and_single_line_description')


class TestMainDescriptionRest(WithSyntaxElementDocumentationBase):
    def runTest(self):
        actual = self.documentation.main_description_rest()
        struct_check.is_paragraph_item_list().apply_without_message(self, actual)


class TestInvokationVariants(WithSyntaxElementDocumentationBase):
    def runTest(self):
        actual = self.documentation.invokation_variants()
        asrt.every_element('invokation_variants', is_invokation_variant).apply_without_message(self, actual)


class TestSeeAlso(WithSyntaxElementDocumentationBase):
    def runTest(self):
        actual = self.documentation.see_also_items()
        asrt.is_list_of(asrt_see_also.is_see_also_item).apply_with_message(self, actual, 'see_also_items')
