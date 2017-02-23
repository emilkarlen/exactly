from exactly_lib.util import line_source


class ListOfLines:
    def __init__(self, lines: iter):
        self.next_line_number = 1
        self.lines = list(lines)

    def has_next(self) -> bool:
        return len(self.lines) > 0

    def next(self) -> line_source.Line:
        ret_val = line_source.Line(self.next_line_number,
                                   self.lines.pop(0))
        self.next_line_number += 1
        return ret_val

    def return_line(self, line: str):
        self.lines.insert(0, line)
        self.next_line_number -= 1

    def forward(self, number_of_lines: int):
        del self.lines[:number_of_lines]
        self.next_line_number += number_of_lines

    def copy(self):
        ret_val = ListOfLines(iter([]))
        ret_val.next_line_number = self.next_line_number
        ret_val.lines = self.lines.copy()
        return ret_val


class LineSequenceSourceFromListOfLines(line_source.LineSequenceSource):
    def __init__(self, list_of_lines: ListOfLines):
        self.list_of_lines = list_of_lines

    def has_next(self) -> bool:
        return self.list_of_lines.has_next()

    def next_line(self) -> str:
        return self.list_of_lines.next().text

    def return_line(self, line: str):
        self.list_of_lines.return_line(line)
