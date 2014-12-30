__author__ = 'emil'


class Phase:
    """
    Class for enumeration of phase constants
    """
    def __init__(self, name: str):
        self._name = name

    def name(self):
        return self._name

SETUP = Phase('setup')
APPLY = Phase('apply')
ASSERT = Phase('assert')
CLEANUP = Phase('cleanup')

ALL = [SETUP, APPLY, ASSERT, CLEANUP]
