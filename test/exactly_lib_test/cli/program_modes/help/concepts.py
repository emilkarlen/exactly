import unittest

from exactly_lib.cli.program_modes.help.concepts import request_rendering
from exactly_lib.cli.program_modes.help.concepts.help_request import ConceptHelpRequest, ConceptHelpItem
from exactly_lib.help.concepts.contents_structure import ConceptsHelp
from exactly_lib.help.utils.render import SectionContentsRenderer
from exactly_lib_test.cli.program_modes.help.argument_parsing import ConceptTestImpl


class TestConceptHelpRequestRendererResolver(unittest.TestCase):
    def test_all_concepts_list(self):
        # ARRANGE #
        concepts = [
            ConceptTestImpl('first'),
            ConceptTestImpl('second'),
        ]
        resolver = request_rendering.ConceptHelpRequestRendererResolver(ConceptsHelp(concepts))
        # ACT #
        actual = resolver.renderer_for(ConceptHelpRequest(ConceptHelpItem.ALL_CONCEPTS_LIST, None))
        # ASSERT #
        self.assertIsInstance(actual, SectionContentsRenderer)

    def test_individual_concept(self):
        # ARRANGE #
        first_concept = ConceptTestImpl('first concept')
        concepts = [
            first_concept,
        ]
        resolver = request_rendering.ConceptHelpRequestRendererResolver(ConceptsHelp(concepts))
        # ACT #
        actual = resolver.renderer_for(ConceptHelpRequest(ConceptHelpItem.INDIVIDUAL_CONCEPT, first_concept))
        # ASSERT #
        self.assertIsInstance(actual, SectionContentsRenderer)


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestConceptHelpRequestRendererResolver))
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
