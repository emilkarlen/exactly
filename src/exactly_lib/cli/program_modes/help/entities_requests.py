from enum import Enum

from exactly_lib.cli.program_modes.help.program_modes.help_request import HelpRequest
from exactly_lib.cli.program_modes.help.program_modes.utils import with_or_without_name
from exactly_lib.help.utils.entity_documentation import EntityDocumentation
from exactly_lib.help.utils.section_contents_renderer import SectionContentsRenderer


class EntityHelpItem(Enum):
    ALL_ENTITIES_LIST = 0
    INDIVIDUAL_ENTITY = 1


class EntityHelpRequest(HelpRequest):
    def __init__(self,
                 entity_type: str,
                 item: EntityHelpItem,
                 individual_entity: EntityDocumentation = None,
                 do_include_name_in_output: bool = False):
        self._entity_type = entity_type
        self._item = item
        self._individual_entity = individual_entity
        self._do_include_name_in_output = do_include_name_in_output

    @property
    def entity_type(self) -> str:
        return self._entity_type

    @property
    def item(self) -> EntityHelpItem:
        return self._item

    @property
    def individual_entity(self) -> EntityDocumentation:
        return self._individual_entity

    @property
    def do_include_name_in_output(self) -> bool:
        return self._do_include_name_in_output


class EntityHelpRequestRendererResolver:
    def __init__(self,
                 individual_entity_renderer_constructor,
                 all_entities_list_renderer_constructor,
                 all_entities: list):
        self.individual_entity_renderer_constructor = individual_entity_renderer_constructor
        self.all_entities_list_renderer_constructor = all_entities_list_renderer_constructor
        self.all_entities = all_entities

    def renderer_for(self, request: EntityHelpRequest) -> SectionContentsRenderer:
        item = request.item
        if item is EntityHelpItem.ALL_ENTITIES_LIST:
            return self.all_entities_list_renderer_constructor(self.all_entities)
        if item is EntityHelpItem.INDIVIDUAL_ENTITY:
            return with_or_without_name(request.do_include_name_in_output,
                                        request.individual_entity.singular_name(),
                                        self.individual_entity_renderer_constructor(request.individual_entity))
        raise ValueError('Invalid %s: %s' % (str(EntityHelpItem), str(item)))
