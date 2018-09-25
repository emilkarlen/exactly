import unittest

from exactly_lib.definitions.entity.all_entity_types import DIRECTIVE_ENTITY_TYPE_NAMES
from exactly_lib.help.entities.directives.contents_structure import DirectiveDocumentation
from exactly_lib_test.common.help.test_resources import see_also_assertions as asrt_see_also
from exactly_lib_test.common.help.test_resources.syntax_contents_structure_assertions import is_invokation_variant, \
    is_syntax_element_description
from exactly_lib_test.definitions.test_resources import cross_reference_id_va as xref_va
from exactly_lib_test.test_resources.test_case_base_with_short_description import \
    TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


def suite_for_directive_documentation(documentation: DirectiveDocumentation) -> unittest.TestSuite:
    return unittest.TestSuite(tcc(documentation) for tcc in [
        TestName,
        TestSingleLineDescriptionStr,
        TestSingleLineDescription,
        TestNameAndSingleLineDescriptionStr,
        TestNameAndSingleLineDescription,
        TestDescription,
        TestInvokationVariants,
        TestSyntaxElements,
        TestSeeAlso,
        TestCrossReferenceTarget,
    ])


class WithDirectiveDocumentationBase(TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType):
    def __init__(self, documentation: DirectiveDocumentation):
        super().__init__(documentation)
        self.documentation = documentation


class TestName(WithDirectiveDocumentationBase):
    def runTest(self):
        actual = self.documentation.singular_name()
        self.assertIsInstance(actual, str, 'name')


class TestSingleLineDescriptionStr(WithDirectiveDocumentationBase):
    def runTest(self):
        actual = self.documentation.single_line_description_str()
        self.assertIsInstance(actual, str, 'single_line_description_str')


class TestSingleLineDescription(WithDirectiveDocumentationBase):
    def runTest(self):
        actual = self.documentation.single_line_description()
        struct_check.is_text.apply_with_message(self, actual, 'single_line_description')


class TestNameAndSingleLineDescriptionStr(WithDirectiveDocumentationBase):
    def runTest(self):
        actual = self.documentation.name_and_single_line_description_str()
        self.assertIsInstance(actual, str, 'name_and_single_line_description_str')


class TestNameAndSingleLineDescription(WithDirectiveDocumentationBase):
    def runTest(self):
        actual = self.documentation.name_and_single_line_description()
        struct_check.is_text.apply_with_message(self, actual, 'name_and_single_line_description')


class TestDescription(WithDirectiveDocumentationBase):
    def runTest(self):
        actual = self.documentation.description()
        struct_check.is_section_contents.apply_with_message(self, actual, 'act_phase_contents')


class TestInvokationVariants(WithDirectiveDocumentationBase):
    def runTest(self):
        actual = self.documentation.invokation_variants()
        asrt.every_element('', is_invokation_variant).apply(self, actual)


class TestSyntaxElements(WithDirectiveDocumentationBase):
    def runTest(self):
        actual = self.documentation.syntax_element_descriptions()
        asrt.every_element('', is_syntax_element_description).apply(self, actual)


class TestSeeAlso(WithDirectiveDocumentationBase):
    def runTest(self):
        actual = self.documentation.see_also_targets()
        asrt_see_also.is_see_also_target_list.apply_with_message(self, actual, 'see_also_items')


class TestCrossReferenceTarget(WithDirectiveDocumentationBase):
    def runTest(self):
        actual = self.documentation.cross_reference_target()
        assertion = xref_va.is_entity_for_type(DIRECTIVE_ENTITY_TYPE_NAMES.identifier)
        assertion.apply_with_message(self, actual, 'cross_reference_target')
