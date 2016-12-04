import unittest

from exactly_lib.help.concepts.contents_structure import ConfigurationParameterDocumentation, Name
from exactly_lib.help.entity_names import CONCEPT_ENTITY_TYPE_NAME
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib_test.help.test_resources import cross_reference_id_va as xref_va
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


def suite_for_plain_concept_documentation(
        documentation: ConfigurationParameterDocumentation) -> unittest.TestSuite:
    return unittest.TestSuite(tcc(documentation) for tcc in [
        TestName,
        TestCrossReferenceTarget,
        TestPurpose,
        TestSummaryParagraphs,
    ])


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


class WithConceptDocumentationBase(unittest.TestCase):
    def __init__(self, documentation):
        super().__init__()
        self.documentation = documentation

    def shortDescription(self):
        return str(type(self)) + '/' + str(type(self.documentation))


class TestName(WithConceptDocumentationBase):
    def runTest(self):
        # ACT #
        name = self.documentation.name()
        # ASSERT #
        self.assertIsInstance(name, Name)
        self.assertIsInstance(name.singular, str)


class TestPurpose(WithConceptDocumentationBase):
    def runTest(self):
        # ACT #
        purpose = self.documentation.purpose()
        # ASSERT #
        self.assertIsInstance(purpose, DescriptionWithSubSections)
        struct_check.is_text.apply(self, purpose.single_line_description)
        struct_check.is_section_contents.apply(self, purpose.rest)


class TestSummaryParagraphs(WithConceptDocumentationBase):
    def runTest(self):
        # ACT #
        paragraphs = self.documentation.summary_paragraphs()
        # ASSERT #
        struct_check.is_paragraph_item_list().apply(self, paragraphs)


class TestCrossReferenceTarget(WithConceptDocumentationBase):
    def runTest(self):
        actual = self.documentation.cross_reference_target()
        assertion = xref_va.is_entity_for_type(CONCEPT_ENTITY_TYPE_NAME)
        assertion.apply_with_message(self, actual, 'cross_reference_target')


class WithConfigurationParameterBase(WithConceptDocumentationBase):
    pass


class TestIsConfigurationParameterInstance(WithConfigurationParameterBase):
    def runTest(self):
        # ACT #
        actual = self.documentation
        # ASSERT #
        self.assertIsInstance(actual, ConfigurationParameterDocumentation)


class TestDefaultValue(WithConfigurationParameterBase):
    def runTest(self):
        # ARRANGE #
        doc = self.documentation
        # ACT & ASSERT #
        self.assertIsInstance(doc.default_value_str(), str)
        struct_check.is_paragraph_item.apply(self, doc.default_value_para())
