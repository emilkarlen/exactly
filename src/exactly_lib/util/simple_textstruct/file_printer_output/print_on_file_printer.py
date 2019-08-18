from typing import Sequence

from exactly_lib.util.simple_textstruct.file_printer_output import printables as ps
from exactly_lib.util.simple_textstruct.file_printer_output.printer import Printable, Printer
from exactly_lib.util.simple_textstruct.structure import ElementProperties, MajorBlock, MinorBlock, \
    LineObjectVisitor, PreFormattedStringLineObject, Document, LineObject, LineElement, StringLineObject, \
    StringLinesObject, FilePrintableLineObject


class BlockSettings:
    def __init__(self,
                 indent: str,
                 separator: Printable,
                 ):
        self.indent = indent
        self.separator = separator


class LayoutSettings:
    def __init__(self,
                 major_block: BlockSettings,
                 minor_block: BlockSettings,
                 line_element_indent: str,
                 ):
        self.major_block = major_block
        self.minor_block = minor_block
        self.line_element_indent = line_element_indent


class PrintablesFactory:
    def __init__(self, settings: LayoutSettings):
        self.settings = settings
        self.line_object_handler = _LineObjectHandler(self)

    def document(self, document: Document) -> Printable:
        return self.major_blocks(document.blocks)

    def major_blocks(self, blocks: Sequence[MajorBlock]) -> Printable:
        return self._blocks(
            self.settings.major_block,
            [
                self.major_block(block)
                for block in blocks
            ]
        )

    def minor_blocks(self, blocks: Sequence[MinorBlock]) -> Printable:
        return self._blocks(
            self.settings.minor_block,
            [
                self.minor_block(block)
                for block in blocks
            ]
        )

    def major_block(self, block: MajorBlock) -> Printable:
        return self._element(block.properties,
                             self.settings.major_block.indent,
                             self.minor_blocks(block.parts)
                             )

    def minor_block(self, block: MinorBlock) -> Printable:
        contents = ps.SequencePrintable([
            self.line_element(line_element)
            for line_element in block.parts
        ])
        return self._element(block.properties,
                             self.settings.minor_block.indent,
                             contents
                             )

    def line_element(self, line_element: LineElement) -> Printable:
        return self._element(
            line_element.properties,
            self.settings.line_element_indent,
            _LineObjectPrintable(self.line_object_handler, line_element.line_object),
        )

    @staticmethod
    def _blocks(settings: BlockSettings,
                parts: Sequence[Printable]) -> Printable:
        return ps.InterspersedSequencePrintable(
            settings.separator,
            parts
        )

    @staticmethod
    def _element(properties: ElementProperties,
                 indent_delta: str,
                 contents: Printable) -> Printable:
        ret_val = contents
        if properties.indented:
            ret_val = ps.IncreasedIndentPrintable(indent_delta,
                                                  ret_val)

        if properties.color is not None:
            ret_val = ps.ColoredPrintable(properties.color,
                                          ret_val)

        if properties.font_style is not None:
            ret_val = ps.FontStyledPrintable(properties.font_style,
                                             ret_val)

        return ret_val


class _LineObjectHandler(LineObjectVisitor[Printer, None]):
    def __init__(self, factory: PrintablesFactory):
        self._factory = factory

    def visit_pre_formatted(self, env: Printer, x: PreFormattedStringLineObject) -> None:
        env.write_non_indented(x.string)
        if not x.string_is_line_ended:
            env.new_line()

    def visit_string(self, env: Printer, x: StringLineObject) -> None:
        env.write_indented(x.string)
        if not x.string_is_line_ended:
            env.new_line()

    def visit_string_lines(self, env: Printer, x: StringLinesObject) -> None:
        for s in x.strings:
            env.write_indented(s)
            env.new_line()

    def visit_file_printable(self, env: Printer, x: FilePrintableLineObject) -> None:
        x.file_printable.print_on(env.file_printer)
        if not x.is_line_ended:
            env.new_line()


class _LineObjectPrintable(Printable):
    def __init__(self,
                 handler: _LineObjectHandler,
                 line_object: LineObject):
        self._handler = handler
        self._line_object = line_object

    def print_on(self, printer: Printer):
        self._line_object.accept(self._handler,
                                 printer)