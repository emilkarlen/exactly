from enum import Enum

from shellcheck_lib.cli.execution_mode.help.mode.help_request import HelpRequest


class MainProgramHelpItem(Enum):
    HELP = 0
    PROGRAM = 1


class MainProgramHelpRequest(HelpRequest):
    def __init__(self,
                 item: MainProgramHelpItem):
        self._item = item

    @property
    def item(self) -> MainProgramHelpItem:
        return self._item
