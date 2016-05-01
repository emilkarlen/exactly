import unittest

from exactly_lib.help.concepts.concept_structure import Name, ConfigurationParameterDocumentation
from exactly_lib.help.utils.description import Description, DescriptionWithSubSections
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


def suite_for_plain_concept_documentation(
        documentation: ConfigurationParameterDocumentation) -> unittest.TestSuite:
    return unittest.TestSuite(tcc(documentation) for tcc in [
        TestName,
        TestPurpose,
        TestSummaryParagraphs,
    ])


def suite_for_configuration_parameter_documentation(
        documentation: ConfigurationParameterDocumentation) -> unittest.TestSuite:
    return unittest.TestSuite(tcc(documentation) for tcc in [
        TestIsConfigurationParameterInstance,
        TestName,
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
