from enum import Enum

from exactly_lib.cli.program_modes.help.program_modes.help_request import HelpRequest


class TestCaseHelpItem(Enum):
    SPECIFICATION = 0
    INSTRUCTION_SET = 1
    PHASE = 2
    INSTRUCTION = 3
    INSTRUCTION_SEARCH = 4
    PHASE_INSTRUCTION_LIST = 5
    CLI_SYNTAX = 6


class TestCaseHelpRequest(HelpRequest):
    def __init__(self,
                 item: TestCaseHelpItem,
                 name: str,
                 value,
                 do_include_name_in_output: bool = False):
        self._item = item
        self._name = name
        self._value = value
        self._do_include_name_in_output = do_include_name_in_output

    @property
    def item(self) -> TestCaseHelpItem:
        return self._item

    @property
    def name(self) -> str:
        return self._name

    @property
    def data(self):
        return self._value

    @property
    def do_include_name_in_output(self) -> bool:
        return self._do_include_name_in_output
