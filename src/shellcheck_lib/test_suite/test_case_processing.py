import enum

from shellcheck_lib.execution.result import FullResult
from shellcheck_lib.test_suite import structure


class TestCaseProcessingStatus(enum.Enum):
    INTERNAL_ERROR = 1
    ACCESS_ERROR = 2
    EXECUTED = 3


class TestCaseAccessError(enum.Enum):
    FILE_ACCESS_ERROR = 1
    PRE_PROCESS_ERROR = 2
    PARSE_ERROR = 3


class TestCaseProcessingResult(tuple):
    def __new__(cls,
                status: TestCaseProcessingStatus,
                message: str=None,
                access_error: TestCaseAccessError=None,
                execution_result: FullResult=None):
        """
        Exactly only one of the arguments must be non-None.
        """
        return tuple.__new__(cls, (status, message, access_error, execution_result))

    @property
    def status(self) -> TestCaseProcessingStatus:
        return self[0]

    @property
    def message(self) -> str:
        return self[1]

    @property
    def access_error(self) -> TestCaseAccessError:
        return self[2]

    @property
    def execution_result(self) -> FullResult:
        return self[3]


def new_internal_error(message: str) -> TestCaseProcessingResult:
    return TestCaseProcessingResult(TestCaseProcessingStatus.INTERNAL_ERROR,
                                    message=message)


def new_access_error(error: TestCaseAccessError) -> TestCaseProcessingResult:
    return TestCaseProcessingResult(TestCaseProcessingStatus.ACCESS_ERROR,
                                    access_error=error)


def new_executed(execution_result: FullResult) -> TestCaseProcessingResult:
    return TestCaseProcessingResult(TestCaseProcessingStatus.EXECUTED,
                                    execution_result=execution_result)


class TestCaseProcessor:
    def apply(self, test_case: structure.TestCase) -> TestCaseProcessingResult:
        raise NotImplementedError()
