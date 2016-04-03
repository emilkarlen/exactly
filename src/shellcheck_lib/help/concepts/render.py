from shellcheck_lib.help.concepts.utils import sorted_concepts_list
from shellcheck_lib.help.program_modes.test_case.contents_structure import ConceptsHelp
from shellcheck_lib.help.utils.render import SectionContentsRenderer
from shellcheck_lib.util.textformat.structure import document as doc


class AllConceptsListRenderer(SectionContentsRenderer):
    def __init__(self, concepts_help: ConceptsHelp):
        self.concepts_help = concepts_help

    def apply(self) -> doc.SectionContents:
        return doc.SectionContents([sorted_concepts_list(self.concepts_help.all_concepts)], [])
