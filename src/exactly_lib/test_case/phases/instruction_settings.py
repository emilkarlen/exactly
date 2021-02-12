from typing import Dict, Optional, Callable

DefaultEnvironGetter = Callable[[], Dict[str, str]]


class InstructionSettings:
    """Properties that an instruction can modify, such that the modifications will affect all future instructions.

    The :class:`InstructionEnvironmentForPreSdsStep` provides read-only access to these properties.
    """

    def __init__(self,
                 environ: Optional[Dict[str, str]],
                 default_environ_getter: DefaultEnvironGetter,
                 ):
        self._environ = environ
        self._default_environ_getter = default_environ_getter

    def environ(self) -> Optional[Dict[str, str]]:
        return self._environ

    def set_environ(self, x: Optional[Dict[str, str]]):
        self._environ = x

    @property
    def default_environ_getter(self) -> DefaultEnvironGetter:
        return self._default_environ_getter
