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

SETUP = Phase('setup')
APPLY = Phase('apply')
ASSERT = Phase('assert')
CLEANUP = Phase('cleanup')

ALL = [SETUP, APPLY, ASSERT, CLEANUP]
