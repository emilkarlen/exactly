import unittest

from shellcheck_lib.general.textformat.structure.paragraph import single_para
from shellcheck_lib.test_case.help.instruction_description import DescriptionWithConstantValues, \
    InvokationVariant, SyntaxElementDescription
from shellcheck_lib.test_case.help.render import instruction as sut
from shellcheck_lib_test.general.textformat.test_resources import structure as struct_check


class TestListItem(unittest.TestCase):
    def test(self):
        actual = sut.instruction_set_list_item(DescriptionWithConstantValues('instruction name',
                                                                             'single line description',
                                                                             '',
                                                                             []))
        struct_check.ListItemChecker(struct_check.CheckerWithMsgPrefix(self)).apply(actual)


class TestManPage(unittest.TestCase):
    def test_just_single_line_description(self):
        description = DescriptionWithConstantValues('instruction name',
                                                    'single line description',
                                                    '',
                                                    [])
        actual = sut.instruction_man_page(description)
        struct_check.section_contents(self, actual)

    def test_with_main_description_rest(self):
        description = DescriptionWithConstantValues('instruction name',
                                                    'single line description',
                                                    'main description rest',
                                                    [])
        actual = sut.instruction_man_page(description)
        struct_check.section_contents(self, actual)

    def test_with_invokation_variants(self):
        description = DescriptionWithConstantValues(
                'instruction name',
                'single line description',
                'main description rest',
                [InvokationVariant('invokation variant syntax',
                                   single_para('invokation variant description rest'))])
        actual = sut.instruction_man_page(description)
        struct_check.section_contents(self, actual)

    def test_with_syntax_elements_without_invokation_variants(self):
        description = DescriptionWithConstantValues(
                'instruction name',
                'single line description',
                'main description rest',
                [InvokationVariant('invokation variant syntax',
                                   single_para('invokation variant description rest'))],
                [SyntaxElementDescription('syntax element',
                                          single_para('description rest'),
                                          [])])
        actual = sut.instruction_man_page(description)
        struct_check.section_contents(self, actual)

    def test_with_syntax_elements_with_invokation_variants(self):
        description = DescriptionWithConstantValues(
                'instruction name',
                'single line description',
                'main description rest',
                [InvokationVariant('invokation variant syntax',
                                   single_para('invokation variant description rest'))],
                [SyntaxElementDescription('syntax element',
                                          single_para('description rest'),
                                          [InvokationVariant('SED/invokation variant syntax',
                                                             single_para('SED/IV description rest'))])])
        actual = sut.instruction_man_page(description)
        struct_check.section_contents(self, actual)


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestListItem))
    ret_val.addTest(unittest.makeSuite(TestManPage))
    return ret_val
