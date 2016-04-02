import unittest

from shellcheck_lib.help.concepts.concept_structure import Name, ConfigurationParameterDocumentation
from shellcheck_lib.help.utils.description import Description
from shellcheck_lib_test.util.textformat.test_resources import structure as struct_check


def suite_for_configuration_parameter_documentation(
        documentation: ConfigurationParameterDocumentation) -> unittest.TestSuite:
    return unittest.TestSuite(tcc(documentation) for tcc in [
        TestName,
        TestName,
        TestPurpose,
        TestDefaultValue,
    ])


def suite_for_plain_concept_documentation(
        documentation: ConfigurationParameterDocumentation) -> unittest.TestSuite:
    return unittest.TestSuite(tcc(documentation) for tcc in [
        TestName,
        TestName,
        TestPurpose,
    ])


class WithConceptDocumentationBase(unittest.TestCase):
    def __init__(self, documentation):
        super().__init__()
        self.documentation = documentation


class TestName(WithConceptDocumentationBase):
    def runTest(self):
        name = self.documentation.name()
        self.assertIsInstance(name, Name)
        self.assertIsInstance(name.singular, str)


class TestPurpose(WithConceptDocumentationBase):
    def runTest(self):
        purpose = self.documentation.purpose()
        self.assertIsInstance(purpose, Description)
        struct_check.is_text.apply(self, purpose.single_line_description)
        struct_check.is_paragraph_item_list().apply(self, purpose.rest)


class WithConfigurationParameterBase(WithConceptDocumentationBase):
    pass


class TestIsConfigurationParameterInstance(WithConfigurationParameterBase):
    def runTest(self):
        actual = self.documentation
        self.assertIsInstance(actual, ConfigurationParameterDocumentation)


class TestDefaultValue(WithConfigurationParameterBase):
    def runTest(self):
        doc = self.documentation
        self.assertIsInstance(doc.default_value_str(), str)
        struct_check.is_paragraph_item.apply(self, doc.default_value_para())
