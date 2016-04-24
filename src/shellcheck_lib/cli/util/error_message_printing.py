import pathlib

from shellcheck_lib.util import line_source
from shellcheck_lib.util.std import FilePrinter


def output_location(printer: FilePrinter,
                    file: pathlib.Path,
                    section_name: str,
                    line: line_source.Line,
                    section_presentation_type_name:str = 'phase'):
    has_output_header = False
    if file:
        printer.write_line('File: ' + str(file))
        has_output_header = True
    if section_name:
        printer.write_line('In %s "%s"' % (section_presentation_type_name, section_name))
        has_output_header = True
    if line:
        printer.write_line('Line {}: `{}\''.format(line.line_number, line.text))
        has_output_header = True

    if has_output_header:
        printer.write_line('')
