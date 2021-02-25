import unittest

from exactly_lib.common.help.syntax_contents_structure import InvokationVariant
from exactly_lib.definitions.cross_ref.concrete_cross_refs import CustomCrossReferenceId
from exactly_lib.definitions.entity.syntax_elements import name_and_ref_target
from exactly_lib.definitions.type_system import TypeCategory
from exactly_lib.help.entities.syntax_elements import render as sut
from exactly_lib.help.entities.syntax_elements.contents_structure import syntax_element_documentation
from exactly_lib.help.entities.syntax_elements.entity_configuration import SYNTAX_ELEMENT_ENTITY_CONFIGURATION
from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib_test.common.test_resources import syntax_parts
from exactly_lib_test.util.textformat.constructor.test_resources import CrossReferenceTextConstructorTestImpl
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestIndividualSyntaxElement),
        unittest.makeSuite(TestAllSyntaxElementsList),
    ])


CONSTRUCTION_ENVIRONMENT = ConstructionEnvironment(CrossReferenceTextConstructorTestImpl())


class TestAllSyntaxElementsList(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        constructor = SYNTAX_ELEMENT_ENTITY_CONFIGURATION.cli_list_constructor_getter.get_constructor(
            [
                syntax_element_documentation(None,
                                             name_and_ref_target('SE1', None, 'single line description of SE1'),
                                             [], (), [], [], []),
                syntax_element_documentation(None,
                                             name_and_ref_target('SE2', None, 'single line description of SE2'),
                                             [], (), [], [], []),
            ])
        # ACT #
        actual = constructor.apply(CONSTRUCTION_ENVIRONMENT)
        # ASSERT #
        struct_check.is_section_contents.apply(self, actual)


class TestIndividualSyntaxElement(unittest.TestCase):
    def runTest(self):
        for type_category in [None, TypeCategory.DATA]:
            nrt = name_and_ref_target('SE1', type_category, 'single line description of SE1')
            test_cases = [
                ('minimal',
                 syntax_element_documentation(nrt.type_category, nrt, [], (), [], [], [])
                 ),
                ('with  main description rest',
                 syntax_element_documentation(nrt.type_category, nrt,
                                              [docs.para('a paragraph')],
                                              (), [], [], [])
                 ),
                ('with  main description rest sub sections',
                 syntax_element_documentation(nrt.type_category, nrt,
                                              [],
                                              [docs.section('a section header', docs.paras('section contents'))],
                                              [], [], [])
                 ),
                ('with  main description rest, and notes',
                 syntax_element_documentation(nrt.type_category, nrt,
                                              [],
                                              [docs.section('a section header', docs.paras('section contents'))],
                                              [], [], [],
                                              docs.section_contents(docs.paras('notes section contents')),
                                              )
                 ),
                ('with invokation variants',
                 syntax_element_documentation(nrt.type_category, nrt, [], (),
                                              syntax_parts.INVOKATION_VARIANTS,
                                              [], [])
                 ),
                ('with syntax element descriptions',
                 syntax_element_documentation(nrt.type_category, nrt, [], (),
                                              [],
                                              syntax_parts.SYNTAX_ELEMENT_DESCRIPTIONS,
                                              [])
                 ),
                ('see also',
                 syntax_element_documentation(nrt.type_category, nrt, [], (), [], [],
                                              [CustomCrossReferenceId('custom-target-name')],
                                              )
                 ),
                ('full',
                 syntax_element_documentation(nrt.type_category, nrt,
                                              [docs.para('a paragraph')],
                                              [docs.section('a section header', docs.paras('section contents'))],
                                              [InvokationVariant('syntax',
                                                                 [docs.para('a paragraph')])],
                                              syntax_parts.SYNTAX_ELEMENT_DESCRIPTIONS,
                                              [CustomCrossReferenceId('custom-target-name')],
                                              docs.section_contents(docs.paras('notes section contents')))
                 ),
            ]
            for test_case_name, documentation in test_cases:
                with self.subTest(test_case_name=test_case_name,
                                  type_category=type_category):
                    # ARRANGE #
                    renderer = sut.IndividualSyntaxElementConstructor(documentation)
                    # ACT #
                    actual = renderer.apply(CONSTRUCTION_ENVIRONMENT)
                    # ASSERT #
                    struct_check.is_article_contents.apply(self, actual)


def _paragraphs() -> list:
    return [docs.para('paragraph text')]


def _sections():
    return [docs.section('header', _paragraphs())]


def _section_contents():
    return docs.section_contents(_paragraphs(), _sections())


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
