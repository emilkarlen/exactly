from typing import Optional, Dict

from exactly_lib.test_case.phases.act.adv_w_validation import AdvWValidation
from exactly_lib.type_val_prims.string_source.string_source import StringSource


class SetupSettingsBuilder:
    def __init__(self,
                 stdin: Optional[AdvWValidation[StringSource]],
                 environ: Optional[Dict[str, str]],
                 ):
        self._stdin = stdin
        self._environ = environ

    @staticmethod
    def new_empty() -> 'SetupSettingsBuilder':
        return SetupSettingsBuilder(None, None)

    @property
    def stdin(self) -> Optional[AdvWValidation[StringSource]]:
        return self._stdin

    @stdin.setter
    def stdin(self, x: Optional[AdvWValidation[StringSource]]):
        self._stdin = x

    @property
    def environ(self) -> Optional[Dict[str, str]]:
        return self._environ

    @environ.setter
    def environ(self, x: Optional[Dict[str, str]]):
        self._environ = x
