from typing import Optional, Mapping

from exactly_lib.type_val_prims.string_source.string_source import StringSource


class AtcExecutionInput(tuple):
    """Configuration of stdin for the act phase, supplied to the ATC by the Actor."""

    def __new__(cls,
                stdin: Optional[StringSource],
                environ: Optional[Mapping[str, str]],
                ):
        return tuple.__new__(cls, (stdin, environ))

    @staticmethod
    def empty() -> 'AtcExecutionInput':
        return AtcExecutionInput(None, None)

    @property
    def stdin(self) -> Optional[StringSource]:
        return self[0]

    @property
    def environ(self) -> Optional[Mapping[str, str]]:
        """
        :return: (immutable) None if inherit current process' environment
        """
        return self[1]
