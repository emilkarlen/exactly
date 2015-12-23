from enum import Enum


class TestCaseHelpItem(Enum):
    OVERVIEW = 0
    INSTRUCTION_SET = 1
    PHASE = 2
    INSTRUCTION = 3
    INSTRUCTION_LIST = 4


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
                 value):
        self._item = item
        self._name = name
        self._value = value

    @property
    def item(self) -> TestCaseHelpItem:
        return self._item

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self):
        return self._value


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
