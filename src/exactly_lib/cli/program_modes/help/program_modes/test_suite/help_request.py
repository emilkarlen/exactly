from enum import Enum

from exactly_lib.cli.program_modes.help.program_modes.help_request import HelpRequest


class TestSuiteHelpItem(Enum):
    OVERVIEW = 0
    SECTION = 1


class TestSuiteHelpRequest(HelpRequest):
    def __init__(self,
                 item: TestSuiteHelpItem,
                 name: str,
                 data
                 ):
        self._item = item
        self._name = name
        self._data = data

    @property
    def item(self) -> TestSuiteHelpItem:
        return self._item

    @property
    def name(self) -> str:
        return self._name

    @property
    def data(self) -> str:
        return self._data
