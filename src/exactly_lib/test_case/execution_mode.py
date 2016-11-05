from enum import Enum


class ExecutionMode(Enum):
    NORMAL = 0
    SKIP = 1
    XFAIL = 2


NAME_NORMAL = 'NORMAL'
NAME_SKIP = 'SKIP'
NAME_XFAIL = 'XFAIL'
NAME_2_MODE = {
    NAME_NORMAL: ExecutionMode.NORMAL,
    NAME_SKIP: ExecutionMode.SKIP,
    NAME_XFAIL: ExecutionMode.XFAIL,
}

NAME_DEFAULT = NAME_NORMAL
