from enum import Enum

from shellcheck_lib.cli.program_modes.help.program_modes.help_request import HelpRequest
from shellcheck_lib.help.concepts.concept_structure import ConceptDocumentation


class ConceptHelpItem(Enum):
    ALL_CONCEPTS_LIST = 0
    INDIVIDUAL_CONCEPT = 1


class ConceptHelpRequest(HelpRequest):
    def __init__(self,
                 item: ConceptHelpItem,
                 individual_concept: ConceptDocumentation):
        self._item = item
        self._individual_concept = individual_concept

    @property
    def item(self) -> ConceptHelpItem:
        return self._item

    @property
    def individual_concept(self) -> ConceptDocumentation:
        return self._individual_concept
