import unittest

from exactly_lib.help.concepts import render as sut
from exactly_lib.help.concepts.all_concepts import all_concepts
from exactly_lib.help.concepts.contents_structure import PlainConceptDocumentation, ConfigurationParameterDocumentation
from exactly_lib.help.concepts.entity_configuration import CONCEPT_ENTITY_CONFIGURATION
from exactly_lib.help.utils.rendering.section_contents_renderer import RenderingEnvironment
from exactly_lib.help_texts.entity.concepts import name_and_ref_target
from exactly_lib.help_texts.name_and_cross_ref import Name
from exactly_lib.util.description import Description, DescriptionWithSubSections, from_simple_description
from exactly_lib.util.textformat.structure.document import SectionContents
from exactly_lib.util.textformat.structure.structures import text, para
from exactly_lib_test.help.test_resources import CrossReferenceTextConstructorTestImpl
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestPlainIndividualConcept),
        unittest.makeSuite(TestIndividualConfigurationParameter),
        unittest.makeSuite(TestAllConceptsList),
    ])


class TestAllConceptsList(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        renderer = CONCEPT_ENTITY_CONFIGURATION.cli_list_renderer_getter.get_render(all_concepts())
        # ACT #
        actual = renderer.apply(RENDERING_ENVIRONMENT)
        # ASSERT #
        struct_check.is_section_contents.apply(self, actual)


class TestPlainIndividualConcept(unittest.TestCase):
    def test_concept_with_only_single_line_description(self):
        # ARRANGE #
        concept = PlainConceptTestImpl(Name('name', 'names'),
                                       Description(text('single line name'),
                                                   []))
        renderer = sut.IndividualConceptRenderer(concept)
        # ACT #
        actual = renderer.apply(RENDERING_ENVIRONMENT)
        # ASSERT #
        struct_check.is_section_contents.apply(self, actual)

    def test_concept_with_complex_description(self):
        # ARRANGE #
        concept = PlainConceptTestImpl(Name('name', 'names'),
                                       Description(text('single line name'),
                                                   [para('rest paragraph')]))
        renderer = sut.IndividualConceptRenderer(concept)
        # ACT #
        actual = renderer.apply(RENDERING_ENVIRONMENT)
        # ASSERT #
        struct_check.is_section_contents.apply(self, actual)


class TestIndividualConfigurationParameter(unittest.TestCase):
    def test_concept_with_only_single_line_description(self):
        # ARRANGE #
        concept = ConfigurationParameterTestImpl(Name('name', 'names'),
                                                 Description(text('single line name'),
                                                             []),
                                                 'default value')
        renderer = sut.IndividualConceptRenderer(concept)
        # ACT #
        actual = renderer.apply(RENDERING_ENVIRONMENT)
        # ASSERT #
        struct_check.is_section_contents.apply(self, actual)

    def test_concept_with_complex_description(self):
        # ARRANGE #
        concept = ConfigurationParameterTestImpl(Name('name', 'names'),
                                                 Description(text('single line name'),
                                                             [para('rest paragraph')]),
                                                 'default value')
        renderer = sut.IndividualConceptRenderer(concept)
        # ACT #
        actual = renderer.apply(RENDERING_ENVIRONMENT)
        # ASSERT #
        struct_check.is_section_contents.apply(self, actual)


class PlainConceptTestImpl(PlainConceptDocumentation):
    def __init__(self,
                 name: Name,
                 description: Description):
        super().__init__(name_and_ref_target(name,
                                             'PlainConceptTestImpl single_line_description'))
        self.description = description

    def purpose(self) -> DescriptionWithSubSections:
        return DescriptionWithSubSections(self.description.single_line_description,
                                          SectionContents(self.description.rest, []))


class ConfigurationParameterTestImpl(ConfigurationParameterDocumentation):
    def __init__(self,
                 name: Name,
                 description: Description,
                 default_value: str):
        super().__init__(name_and_ref_target(name,
                                             'ConfigurationParameterTestImpl single_line_description'))
        self.description = description
        self.default_value = default_value

    def default_value_str(self) -> str:
        return self.default_value

    def purpose(self) -> DescriptionWithSubSections:
        return from_simple_description(self.description)


RENDERING_ENVIRONMENT = RenderingEnvironment(CrossReferenceTextConstructorTestImpl())

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
