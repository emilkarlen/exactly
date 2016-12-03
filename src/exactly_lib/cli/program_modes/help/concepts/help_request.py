from exactly_lib.cli.program_modes.help.entities_requests import EntityHelpRequest, EntityHelpItem
from exactly_lib.help.concepts.contents_structure import ConceptDocumentation
from exactly_lib.help.entity_names import CONCEPT_ENTITY_TYPE_NAME


class ConceptHelpRequest(EntityHelpRequest):
    def __init__(self,
                 item: EntityHelpItem,
                 individual_concept: ConceptDocumentation = None):
        super().__init__(CONCEPT_ENTITY_TYPE_NAME, item, individual_concept)
