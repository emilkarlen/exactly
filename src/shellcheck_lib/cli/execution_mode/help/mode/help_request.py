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
