from enum import IntEnum

from exactly_lib.definitions.test_case import phase_names_plain as names


class PhaseEnum(IntEnum):
    CONFIGURATION = 0
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


CONFIGURATION = Phase(PhaseEnum.CONFIGURATION, names.CONFIGURATION_PHASE_NAME, names.CONFIGURATION_PHASE_NAME)
SETUP = Phase(PhaseEnum.SETUP, names.SETUP_PHASE_NAME, names.SETUP_PHASE_NAME)
ACT = Phase(PhaseEnum.ACT, names.ACT_PHASE_NAME, names.ACT_PHASE_NAME)
BEFORE_ASSERT = Phase(PhaseEnum.BEFORE_ASSERT, names.BEFORE_ASSERT_PHASE_NAME, names.BEFORE_ASSERT_PHASE_NAME)
ASSERT = Phase(PhaseEnum.ASSERT, names.ASSERT_PHASE_NAME, names.ASSERT_PHASE_NAME)
CLEANUP = Phase(PhaseEnum.CLEANUP, names.CLEANUP_PHASE_NAME, names.CLEANUP_PHASE_NAME)

PHASES_FOR_PARTIAL_EXECUTION = (SETUP, ACT, BEFORE_ASSERT, ASSERT, CLEANUP)

ALL = (CONFIGURATION,) + PHASES_FOR_PARTIAL_EXECUTION

ALL_WITH_INSTRUCTIONS = (CONFIGURATION, SETUP, BEFORE_ASSERT, ASSERT, CLEANUP)

DEFAULT_PHASE = ACT
