import unittest

from exactly_lib.definitions.entity.concepts import name_and_ref_target
from exactly_lib.help.entities.concepts import render as sut
from exactly_lib.help.entities.concepts.all_concepts import all_concepts
from exactly_lib.help.entities.concepts.contents_structure import ConceptDocumentation
from exactly_lib.help.entities.concepts.entity_configuration import CONCEPT_ENTITY_CONFIGURATION
from exactly_lib.util.description import Description, DescriptionWithSubSections
from exactly_lib.util.str_.name import Name, NameWithGender, a_name
from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.structure.document import SectionContents
from exactly_lib.util.textformat.structure.structures import text, para
from exactly_lib_test.util.textformat.constructor.test_resources import CrossReferenceTextConstructorTestImpl
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestIndividualConcept),
        unittest.makeSuite(TestList),
    ])


class TestList(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        renderer = CONCEPT_ENTITY_CONFIGURATION.cli_list_constructor_getter.get_constructor(all_concepts())
        # ACT #
        actual = renderer.apply(CONSTRUCTION_ENVIRONMENT)
        # ASSERT #
        struct_check.is_section_contents.apply(self, actual)


class TestIndividualConcept(unittest.TestCase):
    def test_concept_with_only_single_line_description(self):
        # ARRANGE #
        concept = PlainConceptTestImpl(a_name(Name('name', 'names')),
                                       Description(text('single line name'),
                                                   []))
        renderer = sut.IndividualConceptConstructor(concept)
        # ACT #
        actual = renderer.apply(CONSTRUCTION_ENVIRONMENT)
        # ASSERT #
        struct_check.is_article_contents.apply(self, actual)

    def test_concept_with_complex_description(self):
        # ARRANGE #
        concept = PlainConceptTestImpl(a_name(Name('name', 'names')),
                                       Description(text('single line name'),
                                                   [para('rest paragraph')]))
        renderer = sut.IndividualConceptConstructor(concept)
        # ACT #
        actual = renderer.apply(CONSTRUCTION_ENVIRONMENT)
        # ASSERT #
        struct_check.is_article_contents.apply(self, actual)


class PlainConceptTestImpl(ConceptDocumentation):
    def __init__(self,
                 name: NameWithGender,
                 description: Description):
        super().__init__(name_and_ref_target(name,
                                             'PlainConceptTestImpl single_line_description'))
        self.description = description

    def purpose(self) -> DescriptionWithSubSections:
        return DescriptionWithSubSections(self.description.single_line_description,
                                          SectionContents(self.description.rest, []))


CONSTRUCTION_ENVIRONMENT = ConstructionEnvironment(CrossReferenceTextConstructorTestImpl())

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
