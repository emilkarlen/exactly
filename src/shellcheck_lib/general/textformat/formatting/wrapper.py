class Indent(tuple):
    def __new__(cls,
                first_line: str,
                following_lines: str):
        return tuple.__new__(cls, (first_line, following_lines))

    @property
    def first_line(self) -> str:
        return self[0]

    @property
    def following_lines(self) -> str:
        return self[1]
