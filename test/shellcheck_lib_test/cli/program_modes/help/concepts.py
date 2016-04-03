import unittest

from shellcheck_lib.cli.program_modes.help.concepts import request_rendering
from shellcheck_lib.cli.program_modes.help.concepts.help_request import ConceptHelpRequest, ConceptHelpItem
from shellcheck_lib.help.concepts.all_concepts import all_concepts
from shellcheck_lib.help.program_modes.test_case.contents_structure import ConceptsHelp
from shellcheck_lib.help.utils.render import SectionContentsRenderer


class TestConceptHelpRequestRendererResolver(unittest.TestCase):
    def test_all_concepts_list(self):
        # ARRANGE #
        resolver = request_rendering.ConceptHelpRequestRendererResolver(ConceptsHelp(all_concepts()))
        # ACT #
        actual = resolver.renderer_for(ConceptHelpRequest(ConceptHelpItem.ALL_CONCEPTS_LIST, None))
        # ASSERT #
        self.assertIsInstance(actual, SectionContentsRenderer)


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestConceptHelpRequestRendererResolver))
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
