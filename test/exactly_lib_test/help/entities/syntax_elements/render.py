import unittest

from exactly_lib.common.help.syntax_contents_structure import InvokationVariant
from exactly_lib.help.entities.syntax_elements import render as sut
from exactly_lib.help.entities.syntax_elements.contents_structure import syntax_element_documentation
from exactly_lib.help.entities.syntax_elements.entity_configuration import SYNTAX_ELEMENT_ENTITY_CONFIGURATION
from exactly_lib.help.utils.rendering.section_contents_renderer import RenderingEnvironment
from exactly_lib.help_texts.cross_reference_id import CustomCrossReferenceId
from exactly_lib.help_texts.entity.syntax_element import name_and_ref_target
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib_test.common.test_resources import syntax_parts
from exactly_lib_test.help.test_resources import CrossReferenceTextConstructorTestImpl
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestIndividualSyntaxElement),
        unittest.makeSuite(TestAllSyntaxElementsList),
    ])


RENDERING_ENVIRONMENT = RenderingEnvironment(CrossReferenceTextConstructorTestImpl())


class TestAllSyntaxElementsList(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        renderer = SYNTAX_ELEMENT_ENTITY_CONFIGURATION.cli_list_renderer_getter.get_render(
            [
                syntax_element_documentation(name_and_ref_target('SE1', 'single line description of SE1'),
                                             [], [], [], []),
                syntax_element_documentation(name_and_ref_target('SE2', 'single line description of SE2'),
                                             [], [], [], []),
            ])
        # ACT #
        actual = renderer.apply(RENDERING_ENVIRONMENT)
        # ASSERT #
        struct_check.is_section_contents.apply(self, actual)


class TestIndividualSyntaxElement(unittest.TestCase):
    def runTest(self):
        nrt = name_and_ref_target('SE1', 'single line description of SE1')
        test_cases = [
            ('minimal',
             syntax_element_documentation(nrt, [], [], [], [])
             ),
            ('with  main description rest',
             syntax_element_documentation(nrt,
                                          [docs.para('a paragraph')],
                                          [], [], [])
             ),
            ('with invokation variants',
             syntax_element_documentation(nrt, [],
                                          syntax_parts.INVOKATION_VARIANTS,
                                          [], [])
             ),
            ('with syntax element descriptions',
             syntax_element_documentation(nrt, [],
                                          [],
                                          syntax_parts.SYNTAX_ELEMENT_DESCRIPTIONS,
                                          [])
             ),
            ('see_also_specific',
             syntax_element_documentation(nrt, [], [],
                                          [CustomCrossReferenceId('custom-target-name')],
                                          [])
             ),
            ('full',
             syntax_element_documentation(nrt,
                                          [docs.para('a paragraph')],
                                          [InvokationVariant('syntax',
                                                             [docs.para('a paragraph')])],
                                          syntax_parts.SYNTAX_ELEMENT_DESCRIPTIONS,
                                          [CustomCrossReferenceId('custom-target-name')])
             ),
        ]
        for test_case_name, documentation in test_cases:
            with self.subTest(test_case_name=test_case_name):
                # ARRANGE #
                renderer = sut.IndividualSyntaxElementRenderer(documentation)
                # ACT #
                actual = renderer.apply(RENDERING_ENVIRONMENT)
                # ASSERT #
                struct_check.is_section_contents.apply(self, actual)


def _paragraphs() -> list:
    return [docs.para('paragraph text')]


def _sections():
    return [docs.section('header', _paragraphs())]


def _section_contents():
    return docs.section_contents(_paragraphs(), _sections())


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
