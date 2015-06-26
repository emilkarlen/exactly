import enum

from shellcheck_lib.execution.result import FullResult
from shellcheck_lib.test_suite import structure


class TestCaseProcessingStatus(enum.Enum):
    INTERNAL_ERROR = 1
    READ_ERROR = 2
    EXECUTED = 3


class TestCaseReadingError(enum.Enum):
    FILE_ACCESS_ERROR = 1
    PARSE_ERROR = 2


class TestCaseProcessingResult(tuple):
    def __new__(cls,
                status: TestCaseProcessingStatus,
                message: str=None,
                reading_error: TestCaseReadingError=None,
                execution_result: FullResult=None):
        """
        Exactly only one of the arguments must be non-None.
        """
        return tuple.__new__(cls, (status, message, reading_error, execution_result))

    @property
    def status(self) -> TestCaseProcessingStatus:
        return self[0]

    @property
    def message(self) -> str:
        return self[1]

    @property
    def reading_error(self) -> TestCaseReadingError:
        return self[2]

    @property
    def execution_result(self) -> FullResult:
        return self[3]


def new_internal_error(message: str) -> TestCaseProcessingResult:
    return TestCaseProcessingResult(TestCaseProcessingStatus.INTERNAL_ERROR,
                                    message=message)


def new_reading_error(error: TestCaseReadingError) -> TestCaseProcessingResult:
    return TestCaseProcessingResult(TestCaseProcessingStatus.READ_ERROR,
                                    reading_error=error)


def new_executed(execution_result: FullResult) -> TestCaseProcessingResult:
    return TestCaseProcessingResult(TestCaseProcessingStatus.EXECUTED,
                                    execution_result=execution_result)


class TestCaseProcessor:
    def apply(self, test_case: structure.TestCase) -> TestCaseProcessingResult:
        raise NotImplementedError()
