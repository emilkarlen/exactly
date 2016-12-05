from enum import Enum

from exactly_lib.cli.program_modes.help.program_modes.help_request import HelpRequest


class TestSuiteHelpItem(Enum):
    SPECIFICATION = 0
    SECTION = 1
    INSTRUCTION = 3
    CLI_SYNTAX = 6


class TestSuiteHelpRequest(HelpRequest):
    def __init__(self,
                 item: TestSuiteHelpItem,
                 name: str,
                 data,
                 do_include_name_in_output: bool = False):
        self._item = item
        self._name = name
        self._data = data
        self._do_include_name_in_output = do_include_name_in_output

    @property
    def item(self) -> TestSuiteHelpItem:
        return self._item

    @property
    def name(self) -> str:
        return self._name

    @property
    def data(self):
        return self._data

    @property
    def do_include_name_in_output(self) -> bool:
        return self._do_include_name_in_output
