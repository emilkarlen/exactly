import unittest

from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
from exactly_lib_test.common.help.test_resources.see_also_assertions import is_see_also_item
from exactly_lib_test.common.help.test_resources.syntax_contents_structure_assertions import is_invokation_variant, \
    is_syntax_element_description
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


def suite_for_documentation_instance(documentation: InstructionDocumentation) -> unittest.TestSuite:
    return unittest.TestSuite(tcc(documentation) for tcc in [
        TestIsDescriptionInstance
    ])


def suite_for_instruction_documentation(documentation: InstructionDocumentation) -> unittest.TestSuite:
    return unittest.TestSuite(tcc(documentation) for tcc in [
        TestInstructionName,
        TestSingleLineDescription,
        TestMainDescriptionRest,
        TestInvokationVariants,
        TestSyntaxElementDescriptions,
        TestSeeAlsoItems,
    ])


class WithDescriptionBase(unittest.TestCase):
    def __init__(self, description: InstructionDocumentation):
        super().__init__()
        self.description = description

    def shortDescription(self):
        return str(type(self.description))


class TestIsDescriptionInstance(WithDescriptionBase):
    def runTest(self):
        actual = self.description
        self.assertIsInstance(actual, InstructionDocumentation)


class TestInstructionName(WithDescriptionBase):
    def runTest(self):
        actual = self.description.instruction_name()
        self.assertIsInstance(actual, str)


class TestSeeAlsoItems(WithDescriptionBase):
    def runTest(self):
        actual = self.description.see_also_items()
        asrt.every_element('see also items', is_see_also_item).apply(self, actual)


class TestSingleLineDescription(WithDescriptionBase):
    def runTest(self):
        actual = self.description.single_line_description()
        self.assertIsInstance(actual, str)


class TestMainDescriptionRest(WithDescriptionBase):
    def runTest(self):
        actual = self.description.main_description_rest()
        struct_check.is_paragraph_item_list().apply(self, actual)


class TestInvokationVariants(WithDescriptionBase):
    def runTest(self):
        actual = self.description.invokation_variants()
        asrt.every_element('', is_invokation_variant).apply(self, actual)


class TestSyntaxElementDescriptions(WithDescriptionBase):
    def runTest(self):
        actual = self.description.syntax_element_descriptions()
        asrt.every_element('', is_syntax_element_description).apply(self, actual)
