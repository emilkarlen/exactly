import io
import unittest
from typing import TypeVar, Callable, Sequence, List

from exactly_lib.util.ansi_terminal_color import ForegroundColor, FontStyle
from exactly_lib.util.file_printer import FilePrinter
from exactly_lib.util.simple_textstruct import structure as s
from exactly_lib.util.simple_textstruct.file_printer_output.print_on_file_printer import LayoutSettings, BlockSettings, \
    PrintablesFactory
from exactly_lib.util.simple_textstruct.file_printer_output.printer import Printable, Printer
from exactly_lib.util.simple_textstruct.structure import MajorBlock, MinorBlock, LineElement, Document, \
    Indentation
from exactly_lib_test.test_resources.test_utils import NEA

T = TypeVar('T')


def check_line_element(put: unittest.TestCase,
                       to_render: LineElement,
                       expectation: str):
    check(put,
          OBJECT_RENDERER.line_element,
          to_render,
          expectation,
          )


def check_minor_block(put: unittest.TestCase,
                      to_render: MinorBlock,
                      expectation: str):
    check(put,
          OBJECT_RENDERER.minor_block,
          to_render,
          expectation,
          )


def check_minor_blocks(put: unittest.TestCase,
                       to_render: Sequence[MinorBlock],
                       expectation: str):
    check(put,
          OBJECT_RENDERER.minor_blocks,
          to_render,
          expectation,
          )


def check_major_block(put: unittest.TestCase,
                      to_render: MajorBlock,
                      expectation: str):
    check(put,
          OBJECT_RENDERER.major_block,
          to_render,
          expectation,
          )


def check_major_blocks(put: unittest.TestCase,
                       to_render: Sequence[MajorBlock],
                       expectation: str):
    check(put,
          OBJECT_RENDERER.major_blocks,
          to_render,
          expectation,
          )


def check_document(put: unittest.TestCase,
                   to_render: Document,
                   expectation: str):
    check(put,
          OBJECT_RENDERER.document,
          to_render,
          expectation,
          )


def check(put: unittest.TestCase,
          renderer: Callable[[T], Printable],
          to_render: T,
          expected_rendition: str):
    printable = renderer(to_render)
    actual_rendition = _print_to_str(printable)

    put.assertIsInstance(actual_rendition, str, 'rendition must be a str')

    put.assertEqual(expected_rendition,
                    actual_rendition)


LINE_ELEMENT_INDENT = '*'
MINOR_BLOCK_INDENT = '--'
MAJOR_BLOCK_INDENT = '____'
MINOR_BLOCKS_SEPARATOR = '<MINOR_BLOCKS_SEPARATOR>'
MAJOR_BLOCKS_SEPARATOR = '<MAJOR_BLOCKS_SEPARATOR>'


def indentation_cases(indent_str: str) -> List[NEA[str, Indentation]]:
    level_cases = [
        NEA('indentation level of ' + str(level),
            expected=indent_str * level,
            actual=Indentation(level, ''),
            )
        for level in [0, 1, 2]
    ]

    suffix_value = '<indent suffix>'

    suffix_cases = [
        NEA('indentation suffix of ' + suffix_value,
            expected=suffix_value,
            actual=Indentation(0, suffix_value),
            )

    ]
    level_value = 2

    mixed_cases = [
        NEA('indentation level {} and suffix of {}'.format(level_value, suffix_value),
            expected=indent_str * level_value + suffix_value,
            actual=Indentation(level_value, suffix_value),
            )

    ]

    return level_cases + suffix_cases + mixed_cases


class MajorBlocksSeparator(Printable):
    def print_on(self, printer: Printer):
        printer.write_non_indented(MAJOR_BLOCKS_SEPARATOR)
        printer.new_line()


class MinorBlocksSeparator(Printable):
    def print_on(self, printer: Printer):
        printer.write_non_indented(MINOR_BLOCKS_SEPARATOR)
        printer.new_line()


LAYOUT_SETTINGS = LayoutSettings(
    major_block=BlockSettings(MAJOR_BLOCK_INDENT,
                              MajorBlocksSeparator()),
    minor_block=BlockSettings(MINOR_BLOCK_INDENT, MinorBlocksSeparator()),
    line_element_indent=LINE_ELEMENT_INDENT,
)

PRINTABLES_FACTORY = PrintablesFactory(LAYOUT_SETTINGS)


class ObjectRenderer:
    def __init__(self):
        self._factory = PrintablesFactory(LAYOUT_SETTINGS)

    def document(self, document: Document) -> Printable:
        return self._factory.document(document)

    def major_blocks(self, blocks: Sequence[MajorBlock]) -> Printable:
        return self._factory.major_blocks(blocks)

    def minor_blocks(self, blocks: Sequence[MinorBlock]) -> Printable:
        return self._factory.minor_blocks(blocks)

    def major_block(self, block: MajorBlock) -> Printable:
        return self._factory.major_block(block)

    def minor_block(self, block: MinorBlock) -> Printable:
        return self._factory.minor_block(block)

    def line_element(self, line_element: LineElement) -> Printable:
        return self._factory.line_element(line_element)


OBJECT_RENDERER = ObjectRenderer()


def _print_to_str(printable: Printable) -> str:
    output_file = io.StringIO()
    printer = Printer.new(FilePrinterWithTextPropertiesForTest(output_file))

    printable.print_on(printer)

    return output_file.getvalue()


def single_line_element_w_plain_properties(line_contents):
    return s.LineElement(
        s.StringLineObject(line_contents),
        s.ELEMENT_PROPERTIES__NEUTRAL,
    )


class FilePrinterWithTextPropertiesForTest(FilePrinter):
    UNSET_COLOR = 'unset-color'
    UNSET_FONT_STYLE = 'unset-font-style'

    @staticmethod
    def color_string_for(color: ForegroundColor) -> str:
        return str(color)

    @staticmethod
    def font_style_string_for(style: FontStyle) -> str:
        return str(style)

    def set_color(self, color: ForegroundColor):
        self.file.write(self.color_string_for(color))

    def unset_color(self):
        self.file.write(self.UNSET_COLOR)

    def set_font_style(self, style: FontStyle):
        self.file.write(self.font_style_string_for(style))

    def unset_font_style(self):
        self.file.write(self.UNSET_FONT_STYLE)
