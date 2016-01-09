import unittest

from shellcheck_lib.general.textformat.formatting import paragraph_item
from shellcheck_lib.general.textformat.formatting import section
from shellcheck_lib.general.textformat.formatting.wrapper import Wrapper
from shellcheck_lib.test_case.instruction_description import Description, InvokationVariant, \
    SyntaxElementDescription
from shellcheck_lib_test.general.textformat.test_resources import structure as struct_check
from shellcheck_lib_test.test_resources import value_assertion as va


def suite_for_description_instance(description: Description) -> unittest.TestSuite:
    return unittest.TestSuite(tcc(description) for tcc in [
        TestIsDescriptionInstance
    ])


def suite_for_description(description: Description) -> unittest.TestSuite:
    return unittest.TestSuite(tcc(description) for tcc in [
        TestInstructionName,
        TestSingleLineDescription,
        TestMainDescriptionRest,
        TestInvokationVariants,
        TestSyntaxElementDescriptions,
    ])


class WithDescriptionBase(unittest.TestCase):
    def __init__(self, description: Description):
        super().__init__()
        self.description = description


class TestIsDescriptionInstance(WithDescriptionBase):
    def runTest(self):
        actual = self.description
        self.assertIsInstance(actual, Description)


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


class TestDescriptionBase(unittest.TestCase):
    """
    Tests a Description by rendering it with a Formatter
    (under the assumption that the Formatter is working).
    """

    def _description(self) -> Description:
        raise NotImplementedError()

    def setUp(self):
        self.formatter = section.Formatter(paragraph_item.Formatter(Wrapper(page_width=100)))
        self.description = self._description()

    def test_instruction_name(self):
        actual = self.description.instruction_name()
        self.assertIsInstance(actual, str)

    def test_single_line_description(self):
        actual = self.description.single_line_description()
        self.assertIsInstance(actual, str)

    def test_main_description_rest(self):
        actual = self.description.main_description_rest()
        struct_check.paragraph_item_list().apply(self, actual)

    def test_invokation_variants(self):
        actual = self.description.invokation_variants()
        va.every_element('', is_invokation_variant).apply(self, actual)

    def test_syntax_element_descriptions(self):
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
