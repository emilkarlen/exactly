from typing import Mapping, Any

from exactly_lib.util.file_printer import FilePrintable, FilePrinter


def of_constant_string(s: str) -> FilePrintable:
    return _FilePrintableOfConstantString(s)


def of_format_string(format_str: str, format_map: Mapping[str, Any]) -> FilePrintable:
    return _FilePrintableOfFormatString(format_str, format_map)


class _FilePrintableOfConstantString(FilePrintable):
    def __init__(self, s: str):
        self._s = s

    def print_on(self, printer: FilePrinter):
        printer.write(self._s)


class _FilePrintableOfFormatString(FilePrintable):
    def __init__(self, format_str: str, format_map: Mapping[str, Any]):
        self._format_str = format_str
        self._format_map = format_map

    def print_on(self, printer: FilePrinter):
        printer.write(self._format_str.format_map(self._format_map))
