from enum import Enum

from exactly_lib.cli.program_modes.help.program_modes.help_request import HelpRequest


class EntityHelpItem(Enum):
    ALL_ENTITIES_LIST = 0
    INDIVIDUAL_ENTITY = 1


class EntityHelpRequest(HelpRequest):
    def __init__(self,
                 item: EntityHelpItem):
        self._item = item

    @property
    def item(self) -> EntityHelpItem:
        return self._item
