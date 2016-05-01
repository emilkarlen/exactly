from exactly_lib.cli.program_modes.help.concepts.help_request import ConceptHelpRequest, ConceptHelpItem
from exactly_lib.help.concepts.contents_structure import ConceptsHelp
from exactly_lib.help.utils.render import SectionContentsRenderer


class ConceptHelpRequestRendererResolver:
    def __init__(self, concepts_help: ConceptsHelp):
        self.concepts_help = concepts_help

    def renderer_for(self, request: ConceptHelpRequest) -> SectionContentsRenderer:
        from exactly_lib.help.concepts import render
        item = request.item
        if item is ConceptHelpItem.ALL_CONCEPTS_LIST:
            return render.AllConceptsListRenderer(self.concepts_help)
        if item is ConceptHelpItem.INDIVIDUAL_CONCEPT:
            return render.IndividualConceptRenderer(request.individual_concept)
        raise ValueError('Invalid %s: %s' % (str(ConceptHelpItem), str(item)))
