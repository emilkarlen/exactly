from typing import Optional

from exactly_lib.test_case.phases.act.adv_w_validation import AdvWValidation
from exactly_lib.type_val_prims.string_source.string_source import StringSource


class SetupSettingsBuilder:
    def __init__(self):
        self.__stdin = None

    @staticmethod
    def new_empty() -> 'SetupSettingsBuilder':
        return SetupSettingsBuilder()

    @property
    def stdin(self) -> Optional[AdvWValidation[StringSource]]:
        return self.__stdin

    @stdin.setter
    def stdin(self, x: Optional[AdvWValidation[StringSource]]):
        self.__stdin = x
