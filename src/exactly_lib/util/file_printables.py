import itertools
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


def of_newline_ended_items(printable_sequence: Sequence[FilePrintable]) -> FilePrintable:
    printable_list_list = [
        [p, of_new_line()]
        for p in printable_sequence
    ]
    return _FilePrintableSequence(list(itertools.chain.from_iterable(printable_list_list)))


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
