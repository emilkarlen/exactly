from typing import Optional

from exactly_lib.type_val_prims.string_source.string_source import StringSource


class ActExecutionInput(tuple):
    """Configuration of stdin for the act phase, supplied to the ATC by the Actor."""

    def __new__(cls, stdin: Optional[StringSource]):
        return tuple.__new__(cls, (stdin,))

    @staticmethod
    def empty() -> 'ActExecutionInput':
        return ActExecutionInput(None)

    @property
    def stdin(self) -> Optional[StringSource]:
        return self[0]
