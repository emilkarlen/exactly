from enum import Enum


class ExecutionMode(Enum):
    PASS = 0
    SKIP = 1
    FAIL = 2


NAME_PASS = 'PASS'
NAME_SKIP = 'SKIP'
NAME_FAIL = 'FAIL'
NAME_2_STATUS = {
    NAME_PASS: ExecutionMode.PASS,
    NAME_SKIP: ExecutionMode.SKIP,
    NAME_FAIL: ExecutionMode.FAIL,
}

NAME_DEFAULT = NAME_PASS
