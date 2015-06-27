import enum

from shellcheck_lib.execution.result import FullResult
from shellcheck_lib.test_suite import structure


class Status(enum.Enum):
    INTERNAL_ERROR = 1
    ACCESS_ERROR = 2
    EXECUTED = 3


class AccessError(enum.Enum):
    FILE_ACCESS_ERROR = 1
    PRE_PROCESS_ERROR = 2
    PARSE_ERROR = 3


class Result(tuple):
    def __new__(cls,
                status: Status,
                message: str=None,
                access_error: AccessError=None,
                execution_result: FullResult=None):
        """
        Exactly only one of the arguments must be non-None.
        """
        return tuple.__new__(cls, (status, message, access_error, execution_result))

    @property
    def status(self) -> Status:
        return self[0]

    @property
    def message(self) -> str:
        return self[1]

    @property
    def access_error(self) -> AccessError:
        return self[2]

    @property
    def execution_result(self) -> FullResult:
        return self[3]


def new_internal_error(message: str) -> Result:
    return Result(Status.INTERNAL_ERROR,
                  message=message)


def new_access_error(error: AccessError) -> Result:
    return Result(Status.ACCESS_ERROR,
                  access_error=error)


def new_executed(execution_result: FullResult) -> Result:
    return Result(Status.EXECUTED,
                  execution_result=execution_result)


class Processor:
    def apply(self, test_case: structure.TestCase) -> Result:
        raise NotImplementedError()
