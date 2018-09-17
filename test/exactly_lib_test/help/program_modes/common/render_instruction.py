import unittest

from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.help.program_modes.common import render_instruction as sut
from exactly_lib.util.textformat.construction.section_contents.constructor import \
    ConstructionEnvironment
from exactly_lib.util.textformat.structure.structures import paras, text
from exactly_lib_test.common.test_resources.instruction_documentation import InstructionDocumentationWithConstantValues
from exactly_lib_test.util.textformat.construction.test_resources import CrossReferenceTextConstructorTestImpl
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestListItem),
        unittest.makeSuite(TestManPage),
    ])


class TestListItem(unittest.TestCase):
    def test(self):
        actual = sut.instruction_set_list_item(InstructionDocumentationWithConstantValues('instruction name',
                                                                                          'single line description',
                                                                                          '',
                                                                                          []),
                                               text)
        struct_check.is_list_item.apply(self, actual)


class TestManPage(unittest.TestCase):
    def test_just_single_line_description(self):
        description = InstructionDocumentationWithConstantValues('instruction name',
                                                                 'single line description',
                                                                 '',
                                                                 [])
        actual = sut.InstructionDocSectionContentsConstructor(description).apply(CONSTRUCTION_ENVIRONMENT)
        struct_check.is_section_contents.apply(self, actual)

    def test_with_main_description_rest(self):
        description = InstructionDocumentationWithConstantValues('instruction name',
                                                                 'single line description',
                                                                 'main description rest',
                                                                 [])
        actual = sut.InstructionDocSectionContentsConstructor(description).apply(CONSTRUCTION_ENVIRONMENT)
        struct_check.is_section_contents.apply(self, actual)

    def test_with_invokation_variants(self):
        description = InstructionDocumentationWithConstantValues(
            'instruction name',
            'single line description',
            'main description rest',
            [InvokationVariant('invokation variant syntax',
                               paras('invokation variant description rest'))])
        actual = sut.InstructionDocSectionContentsConstructor(description).apply(CONSTRUCTION_ENVIRONMENT)
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
        actual = sut.InstructionDocSectionContentsConstructor(description).apply(CONSTRUCTION_ENVIRONMENT)
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
        actual = sut.InstructionDocSectionContentsConstructor(description).apply(CONSTRUCTION_ENVIRONMENT)
        struct_check.is_section_contents.apply(self, actual)


CONSTRUCTION_ENVIRONMENT = ConstructionEnvironment(CrossReferenceTextConstructorTestImpl())

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
