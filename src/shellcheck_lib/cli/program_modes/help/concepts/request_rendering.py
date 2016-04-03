from shellcheck_lib.cli.program_modes.help.concepts.help_request import ConceptHelpRequest, ConceptHelpItem
from shellcheck_lib.help.program_modes.test_case.contents_structure import ConceptsHelp
from shellcheck_lib.help.utils.render import SectionContentsRenderer


class ConceptHelpRequestRendererResolver:
    def __init__(self, concepts_help: ConceptsHelp):
        self.concepts_help = concepts_help

    def renderer_for(self, request: ConceptHelpRequest) -> SectionContentsRenderer:
        from shellcheck_lib.help.concepts import render
        item = request.item
        if item is ConceptHelpItem.ALL_CONCEPTS_LIST:
            return render.AllConceptsListRenderer(self.concepts_help)
        raise ValueError('Invalid %s: %s' % (str(ConceptHelpRequestRendererResolver), str(item)))
