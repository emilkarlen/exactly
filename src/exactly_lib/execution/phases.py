from enum import Enum


class PhaseEnum(Enum):
    ANONYMOUS = 0
    SETUP = 1
    ACT = 2
    BEFORE_ASSERT = 3
    ASSERT = 4
    CLEANUP = 5


class Phase(tuple):
    """
    Class for enumeration of phase constants
    """

    def __new__(cls,
                the_enum: PhaseEnum,
                section_name: str,
                identifier: str):
        return tuple.__new__(cls, (the_enum, section_name, identifier))

    @property
    def the_enum(self) -> PhaseEnum:
        return self[0]

    @property
    def section_name(self) -> str:
        return self[1]

    @property
    def identifier(self) -> str:
        return self[2]


ANONYMOUS = Phase(PhaseEnum.ANONYMOUS, 'conf', 'conf')
SETUP = Phase(PhaseEnum.SETUP, 'setup', 'setup')
ACT = Phase(PhaseEnum.ACT, 'act', 'act')
BEFORE_ASSERT = Phase(PhaseEnum.BEFORE_ASSERT, 'before-assert', 'before-assert')
ASSERT = Phase(PhaseEnum.ASSERT, 'assert', 'assert')
CLEANUP = Phase(PhaseEnum.CLEANUP, 'cleanup', 'cleanup')

ALL_NAMED = (SETUP, ACT, BEFORE_ASSERT, ASSERT, CLEANUP)

ALL = (ANONYMOUS,) + ALL_NAMED

ALL_WITH_INSTRUCTIONS = (ANONYMOUS, SETUP, BEFORE_ASSERT, ASSERT, CLEANUP)
