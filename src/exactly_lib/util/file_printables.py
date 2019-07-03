import io
from typing import Mapping, Any, Sequence

from exactly_lib.util.file_printer import FilePrintable, FilePrinter


def of_new_line() -> FilePrintable:
    return _NEW_LINE


def of_constant_string(s: str) -> FilePrintable:
    return _FilePrintableOfConstantString(s)


def of_format_string(format_str: str, format_map: Mapping[str, Any]) -> FilePrintable:
    return _FilePrintableOfFormatString(format_str, format_map)


def of_sequence(printable_sequence: Sequence[FilePrintable]) -> FilePrintable:
    return _FilePrintableSequence(printable_sequence)


def of_newline_ended_sequence(printable_sequence: Sequence[FilePrintable]) -> FilePrintable:
    return _FilePrintableSequence(list(printable_sequence) + [_NEW_LINE])


def of_newline_ended_items(items: Sequence[FilePrintable]) -> FilePrintable:
    nl_ended_items = []
    for item in items:
        nl_ended_items += [item, _NEW_LINE]
    return _FilePrintableSequence(nl_ended_items)


def of_newline_separated_items(items: Sequence[FilePrintable]) -> FilePrintable:
    separated_items = items[:1]
    for item in items[1:]:
        separated_items += [_NEW_LINE, item]
    return _FilePrintableSequence(separated_items)


class _FilePrintableOfNewLine(FilePrintable):
    def print_on(self, printer: FilePrinter):
        printer.write_empty_line()


_NEW_LINE = _FilePrintableOfNewLine()


class _FilePrintableOfConstantString(FilePrintable):
    def __init__(self, s: str):
        self._s = s

    def print_on(self, printer: FilePrinter):
        printer.write(self._s)


class _FilePrintableSequence(FilePrintable):
    def __init__(self, printable_sequence: Sequence[FilePrintable]):
        self._printable_sequence = printable_sequence

    def print_on(self, printer: FilePrinter):
        for p in self._printable_sequence:
            p.print_on(printer)


class _FilePrintableOfFormatString(FilePrintable):
    def __init__(self, format_str: str, format_map: Mapping[str, Any]):
        self._format_str = format_str
        self._format_map = format_map

    def print_on(self, printer: FilePrinter):
        printer.write(self._format_str.format_map(self._format_map))


def print_to_string(printable: FilePrintable) -> str:
    mem_file = io.StringIO()
    printable.print_on(FilePrinter(mem_file))
    ret_val = mem_file.getvalue()
    mem_file.close()
    return ret_val
