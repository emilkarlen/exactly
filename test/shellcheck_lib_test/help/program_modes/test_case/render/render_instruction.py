import unittest

from shellcheck_lib.help.program_modes.test_case.instruction_documentation import InvokationVariant, \
    SyntaxElementDescription
from shellcheck_lib.help.program_modes.test_case.render import render_instruction as sut
from shellcheck_lib.util.textformat.structure.structures import paras
from shellcheck_lib_test.test_resources.instruction_description import InstructionDocumentationWithConstantValues
from shellcheck_lib_test.util.textformat.test_resources import structure as struct_check


class TestListItem(unittest.TestCase):
    def test(self):
        actual = sut.instruction_set_list_item(InstructionDocumentationWithConstantValues('instruction name',
                                                                                          'single line description',
                                                                                          '',
                                                                                          []))
        struct_check.is_list_item.apply(self, actual)


class TestManPage(unittest.TestCase):
    def test_just_single_line_description(self):
        description = InstructionDocumentationWithConstantValues('instruction name',
                                                                 'single line description',
                                                                 '',
                                                                 [])
        actual = sut.instruction_man_page(description)
        struct_check.is_section_contents.apply(self, actual)

    def test_with_main_description_rest(self):
        description = InstructionDocumentationWithConstantValues('instruction name',
                                                                 'single line description',
                                                                 'main description rest',
                                                                 [])
        actual = sut.instruction_man_page(description)
        struct_check.is_section_contents.apply(self, actual)

    def test_with_invokation_variants(self):
        description = InstructionDocumentationWithConstantValues(
            'instruction name',
            'single line description',
            'main description rest',
            [InvokationVariant('invokation variant syntax',
                               paras('invokation variant description rest'))])
        actual = sut.instruction_man_page(description)
        struct_check.is_section_contents.apply(self, actual)

    def test_with_syntax_elements_without_invokation_variants(self):
        description = InstructionDocumentationWithConstantValues(
            'instruction name',
            'single line description',
            'main description rest',
            [InvokationVariant('invokation variant syntax',
                               paras('invokation variant description rest'))],
            [SyntaxElementDescription('syntax element',
                                      paras('description rest'),
                                      [])])
        actual = sut.instruction_man_page(description)
        struct_check.is_section_contents.apply(self, actual)

    def test_with_syntax_elements_with_invokation_variants(self):
        description = InstructionDocumentationWithConstantValues(
            'instruction name',
            'single line description',
            'main description rest',
            [InvokationVariant('invokation variant syntax',
                               paras('invokation variant description rest'))],
            [SyntaxElementDescription('syntax element',
                                      paras('description rest'),
                                      [InvokationVariant('SED/invokation variant syntax',
                                                         paras('SED/IV description rest'))])])
        actual = sut.instruction_man_page(description)
        struct_check.is_section_contents.apply(self, actual)


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestListItem),
        unittest.makeSuite(TestManPage),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
