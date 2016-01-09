import unittest

from shellcheck_lib.general.textformat.formatting import paragraph_item
from shellcheck_lib.general.textformat.formatting import section
from shellcheck_lib.general.textformat.formatting.wrapper import Wrapper
from shellcheck_lib.test_case.instruction_description import Description, InvokationVariant, \
    SyntaxElementDescription
from shellcheck_lib_test.general.textformat.test_resources import structure as struct_check


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
        struct_check.paragraph_item_list(self, actual)


class TestInvokationVariants(WithDescriptionBase):
    def runTest(self):
        actual = self.description.invokation_variants()
        struct_check.check_list(InvokationVariantChecker,
                                struct_check.CheckerWithMsgPrefix(self),
                                actual)


class TestSyntaxElementDescriptions(WithDescriptionBase):
    def runTest(self):
        actual = self.description.syntax_element_descriptions()
        struct_check.check_list(SyntaxElementDescriptionChecker,
                                struct_check.CheckerWithMsgPrefix(self),
                                actual)


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
        struct_check.paragraph_item_list(self, actual)

    def test_invokation_variants(self):
        actual = self.description.invokation_variants()
        struct_check.check_list(InvokationVariantChecker,
                                struct_check.CheckerWithMsgPrefix(self),
                                actual)

    def test_syntax_element_descriptions(self):
        actual = self.description.syntax_element_descriptions()
        struct_check.check_list(SyntaxElementDescriptionChecker,
                                struct_check.CheckerWithMsgPrefix(self),
                                actual)


class InvokationVariantChecker(struct_check.Assertion):
    def __init__(self,
                 checker: struct_check.CheckerWithMsgPrefix):
        self.checker = checker

    def apply(self, x):
        self.checker.put.assertIsInstance(x,
                                          InvokationVariant,
                                          self.checker.msg('Must be instance of %s' % InvokationVariant))
        assert isinstance(x, InvokationVariant)
        self.checker.put.assertIsInstance(x.syntax,
                                          str,
                                          self.checker.msg('syntax be instance of %s' % str))
        struct_check.check_list(struct_check.ParagraphItemChecker,
                                struct_check.new_with_added_prefix('description_rest', self.checker),
                                x.description_rest)


class SyntaxElementDescriptionChecker(struct_check.Assertion):
    def __init__(self,
                 checker: struct_check.CheckerWithMsgPrefix):
        self.checker = checker

    def apply(self, x):
        self.checker.put.assertIsInstance(x,
                                          SyntaxElementDescription,
                                          self.checker.msg('Must be instance of %s' % SyntaxElementDescription))
        assert isinstance(x, SyntaxElementDescription)
        self.checker.put.assertIsInstance(x.element_name,
                                          str,
                                          self.checker.msg('element_name be instance of %s' % str))
        struct_check.check_list(struct_check.ParagraphItemChecker,
                                struct_check.new_with_added_prefix('description_rest', self.checker),
                                x.description_rest)
        struct_check.check_list(InvokationVariantChecker,
                                struct_check.new_with_added_prefix('invokation_variants: ', self.checker),
                                x.invokation_variants)
