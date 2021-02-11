from typing import Dict, Optional, Mapping


class InstructionSettings:
    """Properties that an instruction can modify, such that the modifications will affect all future instructions.

    The :class:`InstructionEnvironmentForPreSdsStep` provides read-only access to these properties.
    """

    def __init__(self, environ: Optional[Dict[str, str]]):
        self._environ = environ

    @staticmethod
    def of_copy(environ: Optional[Mapping[str, str]]) -> 'InstructionSettings':
        return InstructionSettings(
            None
            if environ is None
            else
            dict(environ)
        )

    def environ(self) -> Optional[Dict[str, str]]:
        return self._environ

    def set_environ(self, x: Optional[Dict[str, str]]):
        self._environ = x
