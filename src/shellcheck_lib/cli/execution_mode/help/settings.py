from enum import Enum

from shellcheck_lib.test_case.help.instruction_description import Description


class TestCaseHelpItem(Enum):
    OVERVIEW = 0
    INSTRUCTION_SET = 1
    PHASE = 2
    INSTRUCTION = 3


class TestSuiteHelpItem(Enum):
    OVERVIEW = 0
    SECTION = 1


class HelpSettings:
    pass


class ProgramHelpSettings(HelpSettings):
    pass


class TestCaseHelpSettings(HelpSettings):
    def __init__(self,
                 item: TestCaseHelpItem,
                 name: str,
                 instruction_description: Description):
        self._item = item
        self._name = name
        self._instruction_description = instruction_description

    @property
    def item(self) -> TestCaseHelpItem:
        return self._item

    @property
    def name(self) -> str:
        return self._name

    @property
    def instruction_description(self) -> Description:
        return self._instruction_description


class TestSuiteHelpSettings(HelpSettings):
    def __init__(self,
                 item: TestSuiteHelpItem,
                 name: str,
                 ):
        self._item = item
        self._name = name

    @property
    def item(self) -> TestSuiteHelpItem:
        return self._item

    @property
    def name(self) -> str:
        return self._name
