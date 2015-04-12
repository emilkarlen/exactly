__author__ = 'emil'


class Phase(tuple):
    """
    Class for enumeration of phase constants
    """
    def __new__(cls,
                name: str):
        return tuple.__new__(cls, (name, ))

    @property
    def name(self) -> str:
        return self[0]

ANONYMOUS = Phase(None)
SETUP = Phase('setup')
ACT = Phase('act')
ASSERT = Phase('assert')
CLEANUP = Phase('cleanup')

ALL_NAMED = [SETUP, ACT, ASSERT, CLEANUP]
