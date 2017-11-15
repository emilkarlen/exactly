import unittest

from exactly_lib.help.entities.configuration_parameters.contents_structure import ConfigurationParameterDocumentation
from exactly_lib.help_texts.entity_identifiers import CONFIGURATION_PARAMETER_ENTITY_TYPE_IDENTIFIER
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib_test.help_texts.test_resources import cross_reference_id_va as xref_va
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


def suite_for_configuration_parameter_documentation(
        documentation: ConfigurationParameterDocumentation) -> unittest.TestSuite:
    return unittest.TestSuite(tcc(documentation) for tcc in [
        TestIsConfigurationParameterInstance,
        TestName,
        TestCrossReferenceTarget,
        TestPurpose,
        TestDefaultValue,
        TestSummaryParagraphs,
    ])


class WithDocumentationBase(unittest.TestCase):
    def __init__(self, documentation: ConfigurationParameterDocumentation):
        super().__init__()
        self.documentation = documentation

    def shortDescription(self):
        return str(type(self)) + '/' + str(type(self.documentation))


class TestName(WithDocumentationBase):
    def runTest(self):
        # ACT #
        name = self.documentation.singular_name()
        # ASSERT #
        self.assertIsInstance(name, str)


class TestPurpose(WithDocumentationBase):
    def runTest(self):
        # ACT #
        purpose = self.documentation.purpose()
        # ASSERT #
        self.assertIsInstance(purpose, DescriptionWithSubSections)
        struct_check.is_text.apply(self, purpose.single_line_description)
        struct_check.is_section_contents.apply(self, purpose.rest)


class TestSummaryParagraphs(WithDocumentationBase):
    def runTest(self):
        # ACT #
        paragraphs = self.documentation.summary_paragraphs()
        # ASSERT #
        struct_check.is_paragraph_item_list().apply(self, paragraphs)


class TestCrossReferenceTarget(WithDocumentationBase):
    def runTest(self):
        actual = self.documentation.cross_reference_target()
        assertion = xref_va.is_entity_for_type(CONFIGURATION_PARAMETER_ENTITY_TYPE_IDENTIFIER)
        assertion.apply_with_message(self, actual, 'cross_reference_target')


class TestIsConfigurationParameterInstance(WithDocumentationBase):
    def runTest(self):
        # ACT #
        actual = self.documentation
        # ASSERT #
        self.assertIsInstance(actual, ConfigurationParameterDocumentation)


class TestDefaultValue(WithDocumentationBase):
    def runTest(self):
        # ARRANGE #
        doc = self.documentation
        # ACT & ASSERT #
        self.assertIsInstance(doc.default_value_str(), str)
        struct_check.is_paragraph_item.apply(self, doc.default_value_para())
