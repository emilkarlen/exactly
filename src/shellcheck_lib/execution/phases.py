class Phase(tuple):
    """
    Class for enumeration of phase constants
    """

    def __new__(cls,
                section_name: str,
                identifier: str):
        return tuple.__new__(cls, (section_name, identifier))

    @property
    def section_name(self) -> str:
        return self[0]

    @property
    def identifier(self) -> str:
        return self[1]


ANONYMOUS = Phase(None, 'configuration')
SETUP = Phase('setup', 'setup')
ACT = Phase('act', 'act')
BEFORE_ASSERT = Phase('before-assert', 'before-assert')
ASSERT = Phase('assert', 'assert')
CLEANUP = Phase('cleanup', 'cleanup')

ALL_NAMED = (SETUP, ACT, BEFORE_ASSERT, ASSERT, CLEANUP)

ALL = (ANONYMOUS,) + ALL_NAMED

ALL_WITH_INSTRUCTIONS = (ANONYMOUS, SETUP, BEFORE_ASSERT, ASSERT, CLEANUP)
