from exactly_lib.test_case.phases.common import TestCaseInstruction
from exactly_lib.util.line_source import LineSequence


class ActPhaseInstruction(TestCaseInstruction):
    """
    Abstract base class for instructions of the ACT phase.
    """

    def source_code(self) -> LineSequence:
        raise NotImplementedError('abstract method')
