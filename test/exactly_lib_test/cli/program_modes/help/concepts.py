import unittest

from exactly_lib.cli.program_modes.help import concepts as sut
from exactly_lib.cli.program_modes.help.entities_requests import EntityHelpItem, EntityHelpRequest
from exactly_lib.help.concepts.contents_structure import concepts_help, ConceptDocumentation
from exactly_lib.help.entity_names import CONCEPT_ENTITY_TYPE_NAME
from exactly_lib.help.utils.section_contents_renderer import SectionContentsRenderer
from exactly_lib_test.help.concepts.test_resources.documentation import ConceptTestImpl
from exactly_lib_test.help.test_resources.rendering_environment import RENDERING_ENVIRONMENT
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestConceptHelpRequestRendererResolver)


class TestConceptHelpRequestRendererResolver(unittest.TestCase):
    def test_all_concepts_list(self):
        # ARRANGE #
        concepts = [
            ConceptTestImpl('first'),
            ConceptTestImpl('second'),
        ]
        resolver = sut.concept_help_request_renderer_resolver(concepts_help(concepts))
        # ACT #
        actual = resolver.renderer_for(_concept_help_request(EntityHelpItem.ALL_ENTITIES_LIST, None))
        # ASSERT #
        self.assertIsInstance(actual, SectionContentsRenderer)
        section_contents = actual.apply(RENDERING_ENVIRONMENT)
        struct_check.is_section_contents.apply_with_message(self, section_contents,
                                                            'output from renderer')

    def test_individual_concept(self):
        # ARRANGE #
        first_concept = ConceptTestImpl('first concept')
        concepts = [
            first_concept,
        ]
        resolver = sut.concept_help_request_renderer_resolver(concepts_help(concepts))
        # ACT #
        actual = resolver.renderer_for(_concept_help_request(EntityHelpItem.INDIVIDUAL_ENTITY,
                                                             first_concept,
                                                             do_include_name_in_output=False))
        # ASSERT #
        self.assertIsInstance(actual, SectionContentsRenderer)
        section_contents = actual.apply(RENDERING_ENVIRONMENT)
        struct_check.is_section_contents.apply_with_message(self, section_contents,
                                                            'output from renderer')

    def test_individual_concept_and_include_name_in_output(self):
        # ARRANGE #
        first_concept = ConceptTestImpl('first concept')
        concepts = [
            first_concept,
        ]
        resolver = sut.concept_help_request_renderer_resolver(concepts_help(concepts))
        # ACT #
        actual = resolver.renderer_for(_concept_help_request(EntityHelpItem.INDIVIDUAL_ENTITY,
                                                             first_concept,
                                                             do_include_name_in_output=True))
        # ASSERT #
        self.assertIsInstance(actual, SectionContentsRenderer)
        section_contents = actual.apply(RENDERING_ENVIRONMENT)
        struct_check.is_section_contents.apply_with_message(self, section_contents,
                                                            'output from renderer')


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())


def _concept_help_request(item: EntityHelpItem,
                          individual_concept: ConceptDocumentation = None,
                          do_include_name_in_output: bool = False) -> EntityHelpRequest:
    return EntityHelpRequest(CONCEPT_ENTITY_TYPE_NAME, item, individual_concept,
                             do_include_name_in_output)
