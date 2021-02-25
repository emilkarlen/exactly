import unittest

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.entity import types
from exactly_lib.definitions.type_system import TypeCategory
from exactly_lib.help.entities.types import all_types
from exactly_lib.help.entities.types import render as sut
from exactly_lib.help.entities.types.contents_structure import TypeDocumentation
from exactly_lib.help.entities.types.entity_configuration import TYPE_ENTITY_CONFIGURATION
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.str_.name import a_name_with_plural_s
from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.document import empty_section_contents
from exactly_lib_test.util.textformat.constructor.test_resources import CrossReferenceTextConstructorTestImpl
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestIndividualType),
        unittest.makeSuite(TestList),
    ])


class TestList(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        renderer = TYPE_ENTITY_CONFIGURATION.cli_list_constructor_getter.get_constructor(
            all_types.all_types())
        # ACT #
        actual = renderer.apply(CONSTRUCTION_ENVIRONMENT)
        # ASSERT #
        struct_check.is_section_contents.apply(self, actual)


class TestIndividualType(unittest.TestCase):
    def test_with_empty_main_description(self):
        # ARRANGE #
        for type_cat_case in SYNTAX_ELEM_TYPE_CATEGORY_CASES:
            doc = TypeDocumentation(A_TYPE_NAME_AND_CROSS_REFERENCE_ID,
                                    type_cat_case.value,
                                    empty_section_contents())
            renderer = sut.IndividualTypeConstructor(doc)
            with self.subTest(type_cat_case.name):
                # ACT #
                actual = renderer.apply(CONSTRUCTION_ENVIRONMENT)
                # ASSERT #
                struct_check.is_article_contents.apply(self, actual)

    def test_with_non_empty_main_description(self):
        # ARRANGE #
        for type_cat_case in SYNTAX_ELEM_TYPE_CATEGORY_CASES:
            doc = TypeDocumentation(A_TYPE_NAME_AND_CROSS_REFERENCE_ID,
                                    type_cat_case.value,
                                    docs.section_contents(docs.paras('initial paragraphs of main description')))
            renderer = sut.IndividualTypeConstructor(doc)
            with self.subTest(type_cat_case.name):
                # ACT #
                actual = renderer.apply(CONSTRUCTION_ENVIRONMENT)
                # ASSERT #
                struct_check.is_article_contents.apply(self, actual)


A_SYNTAX_ELEMENT_INFO__WO_TYPE_CATEGORY = syntax_elements.SyntaxElementInfo(
    'syntax_element_sing_name',
    None,
    'syntax element single line description',
    syntax_elements.syntax_element_cross_ref(
        'syntax_element_sing_name')
)

A_SYNTAX_ELEMENT_INFO__W_TYPE_CATEGORY = syntax_elements.SyntaxElementInfo(
    'syntax_element_sing_name',
    TypeCategory.LOGIC,
    'syntax element single line description',
    syntax_elements.syntax_element_cross_ref(
        'syntax_element_sing_name')
)

SYNTAX_ELEM_TYPE_CATEGORY_CASES = [
    NameAndValue(
        'wo type category',
        A_SYNTAX_ELEMENT_INFO__WO_TYPE_CATEGORY,
    ),
    NameAndValue(
        'w type category',
        A_SYNTAX_ELEMENT_INFO__W_TYPE_CATEGORY,
    ),
]

A_TYPE_NAME_AND_CROSS_REFERENCE_ID = types.name_and_ref_target(ValueType.STRING,
                                                               TypeCategory.DATA,
                                                               a_name_with_plural_s('type_name'),
                                                               'single line description')

CONSTRUCTION_ENVIRONMENT = ConstructionEnvironment(CrossReferenceTextConstructorTestImpl())

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
