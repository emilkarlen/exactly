import unittest

from shellcheck_lib.test_case.instruction_documentation import InstructionReference, InvokationVariant, \
    SyntaxElementDescription
from shellcheck_lib_test.test_resources import value_assertion as va
from shellcheck_lib_test.util.textformat.test_resources import structure as struct_check


def suite_for_description_instance(description: InstructionReference) -> unittest.TestSuite:
    return unittest.TestSuite(tcc(description) for tcc in [
        TestIsDescriptionInstance
    ])


def suite_for_description(description: InstructionReference) -> unittest.TestSuite:
    return unittest.TestSuite(tcc(description) for tcc in [
        TestInstructionName,
        TestSingleLineDescription,
        TestMainDescriptionRest,
        TestInvokationVariants,
        TestSyntaxElementDescriptions,
    ])


class WithDescriptionBase(unittest.TestCase):
    def __init__(self, description: InstructionReference):
        super().__init__()
        self.description = description


class TestIsDescriptionInstance(WithDescriptionBase):
    def runTest(self):
        actual = self.description
        self.assertIsInstance(actual, InstructionReference)


class TestInstructionName(WithDescriptionBase):
    def runTest(self):
        actual = self.description.instruction_name()
        self.assertIsInstance(actual, str)


class TestSingleLineDescription(WithDescriptionBase):
    def runTest(self):
        actual = self.description.single_line_description()
        self.assertIsInstance(actual, str)


class TestMainDescriptionRest(WithDescriptionBase):
    def runTest(self):
        actual = self.description.main_description_rest()
        struct_check.paragraph_item_list().apply(self, actual)


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
