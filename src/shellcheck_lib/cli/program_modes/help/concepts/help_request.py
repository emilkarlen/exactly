from enum import Enum

from shellcheck_lib.cli.program_modes.help.program_modes.help_request import HelpRequest


class ConceptHelpItem(Enum):
    ALL_CONCEPTS_LIST = 0
    INDIVIDUAL_CONCEPT = 1


class ConceptHelpRequest(HelpRequest):
    def __init__(self,
                 item: ConceptHelpItem,
                 individual_concept_name: str):
        self._item = item
        self._individual_concept_name = individual_concept_name

    @property
    def item(self) -> ConceptHelpItem:
        return self._item

    @property
    def individual_concept_name(self) -> str:
        return self._individual_concept_name
