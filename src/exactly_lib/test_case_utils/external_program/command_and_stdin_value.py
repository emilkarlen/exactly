from typing import Sequence

from exactly_lib.test_case_utils.external_program.command.command_value import CommandValue
from exactly_lib.test_case_utils.util_values import StringOrFileRefValue


class CommandAndStdinValue:
    """
    A command together with stdin contents.
    """

    def __init__(self,
                 command: CommandValue,
                 stdin_fragments: Sequence[StringOrFileRefValue]):
        self._stdin_fragments = stdin_fragments
        self._command = command

    @property
    def command(self) -> CommandValue:
        return self._command

    @property
    def stdin_fragments(self) -> Sequence[StringOrFileRefValue]:
        return self._stdin_fragments
