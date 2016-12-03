import unittest

from exactly_lib.cli.program_modes.help import concepts as sut
from exactly_lib.cli.program_modes.help.entities_requests import EntityHelpItem, EntityHelpRequest
from exactly_lib.help.concepts.contents_structure import concepts_help, ConceptDocumentation
from exactly_lib.help.entity_names import CONCEPT_ENTITY_TYPE_NAME
from exactly_lib.help.utils.render import SectionContentsRenderer
from exactly_lib_test.help.concepts.test_resources.documentation import ConceptTestImpl


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

    def test_individual_concept(self):
        # ARRANGE #
        first_concept = ConceptTestImpl('first concept')
        concepts = [
            first_concept,
        ]
        resolver = sut.concept_help_request_renderer_resolver(concepts_help(concepts))
        # ACT #
        actual = resolver.renderer_for(_concept_help_request(EntityHelpItem.INDIVIDUAL_ENTITY, first_concept))
        # ASSERT #
        self.assertIsInstance(actual, SectionContentsRenderer)


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestConceptHelpRequestRendererResolver))
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())


def _concept_help_request(item: EntityHelpItem,
                          individual_concept: ConceptDocumentation = None) -> EntityHelpRequest:
    return EntityHelpRequest(CONCEPT_ENTITY_TYPE_NAME, item, individual_concept)
