from exactly_lib.util.ansi_terminal_color import ForegroundColor


class ExitValue(tuple):
    """
    Result reporting of a process by an exit code together with an
    corresponding identifier on stdout.
    """

    def __new__(cls,
                exit_code: int,
                exit_identifier: str,
                color: ForegroundColor):
        return tuple.__new__(cls, (exit_code, exit_identifier, color))

    @property
    def exit_code(self) -> int:
        return self[0]

    @property
    def exit_identifier(self) -> str:
        return self[1]

    @property
    def color(self) -> ForegroundColor:
        return self[2]

    def __hash__(self) -> int:
        return self.exit_code

    def __eq__(self, o: object) -> bool:
        return isinstance(o, ExitValue) and o.exit_code == self.exit_code
