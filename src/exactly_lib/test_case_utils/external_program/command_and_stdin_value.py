from exactly_lib.test_case_utils.external_program.command.command_value import CommandValue
from exactly_lib.test_case_utils.external_program.component_values import StdinDataValue


class CommandAndStdinValue:
    """
    A command together with stdin contents.
    """

    def __init__(self,
                 command: CommandValue,
                 stdin: StdinDataValue):
        self._stdin = stdin
        self._command = command

    @property
    def command(self) -> CommandValue:
        return self._command

    @property
    def stdin(self) -> StdinDataValue:
        return self._stdin
