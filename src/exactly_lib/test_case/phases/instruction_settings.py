from typing import Dict, Optional

from exactly_lib.test_case.phases.environ import DefaultEnvironGetter


class InstructionSettings:
    """Properties that an instruction can modify, such that the modifications will affect all future instructions.

    The :class:`InstructionEnvironmentForPreSdsStep` provides read-only access to these properties.
    """

    def __init__(self,
                 environ: Optional[Dict[str, str]],
                 default_environ_getter: DefaultEnvironGetter,
                 timeout_in_seconds: Optional[int],
                 ):
        self._environ = environ
        self._default_environ_getter = default_environ_getter
        self._timeout_in_seconds = timeout_in_seconds

    def timeout_in_seconds(self) -> Optional[int]:
        return self._timeout_in_seconds

    def set_timeout(self, seconds: Optional[int]):
        self._timeout_in_seconds = seconds

    def environ(self) -> Optional[Dict[str, str]]:
        return self._environ

    def set_environ(self, x: Optional[Dict[str, str]]):
        self._environ = x

    @property
    def default_environ_getter(self) -> DefaultEnvironGetter:
        return self._default_environ_getter
