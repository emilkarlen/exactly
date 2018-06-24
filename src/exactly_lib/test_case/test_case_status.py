from enum import Enum


class TestCaseStatus(Enum):
    PASS = 0
    SKIP = 1
    FAIL = 2


NAME_PASS = 'PASS'
NAME_SKIP = 'SKIP'
NAME_FAIL = 'FAIL'

NAME_2_STATUS = {
    NAME_PASS: TestCaseStatus.PASS,
    NAME_SKIP: TestCaseStatus.SKIP,
    NAME_FAIL: TestCaseStatus.FAIL,
}

NAME_DEFAULT = NAME_PASS
