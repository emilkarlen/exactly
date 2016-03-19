from enum import Enum


class HelpRequest:
    """
    A request for help of a subject.
    E.g. the instruction "my-instr" in the phase "my-phase" of the execution mode "test-case".
    """
    pass


class ProgramHelpItem(Enum):
    HELP = 0
    PROGRAM = 1


class ProgramHelpRequest(HelpRequest):
    def __init__(self,
                 item: ProgramHelpItem):
        self._item = item

    @property
    def item(self) -> ProgramHelpItem:
        return self._item


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
