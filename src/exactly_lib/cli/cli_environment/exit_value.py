class ExitValue(tuple):
    def __new__(cls,
                exit_code: int,
                exit_identifier: str):
        return tuple.__new__(cls, (exit_code, exit_identifier))

    @property
    def exit_code(self) -> int:
        return self[0]

    @property
    def exit_identifier(self) -> str:
        return self[1]
