import unittest

from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib_test.common.help.test_resources.see_also_va import is_see_also_item
from exactly_lib_test.test_resources.value_assertions import value_assertion as va
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
        va.every_element('see also items', is_see_also_item).apply(self, actual)


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
        va.every_element('', is_invokation_variant).apply(self, actual)


class TestSyntaxElementDescriptions(WithDescriptionBase):
    def runTest(self):
        actual = self.description.syntax_element_descriptions()
        va.every_element('', syntax_element_description_checker).apply(self, actual)


is_invokation_variant = va.And([
    va.IsInstance(InvokationVariant),
    va.sub_component('syntax',
                     lambda x: x.syntax,
                     va.IsInstance(str)),
    va.sub_component_list('description_rest',
                          lambda x: x.description_rest,
                          struct_check.is_paragraph_item)
])

syntax_element_description_checker = va.And([
    va.IsInstance(SyntaxElementDescription),
    va.sub_component('name',
                     lambda x: x.element_name,
                     va.IsInstance(str)),
    va.sub_component_list('description_rest',
                          lambda x: x.description_rest,
                          struct_check.is_paragraph_item)
])
