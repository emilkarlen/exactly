from typing import Sequence

from exactly_lib.util.simple_textstruct.render import printables as ps
from exactly_lib.util.simple_textstruct.render.printer import Printable, Printer
from exactly_lib.util.simple_textstruct.structure import LineObject, BlockProperties, MajorBlock, MinorBlock, \
    LineObjectVisitor, PreFormattedStringLineObject

_NEW_LINE_PRINTABLE = ps.NewLinePrintable()

_MAJOR_BLOCK_SEPARATOR_PRINTABLE = ps.SequencePrintable([_NEW_LINE_PRINTABLE,
                                                         _NEW_LINE_PRINTABLE])

_MINOR_BLOCK_SEPARATOR_PRINTABLE = _NEW_LINE_PRINTABLE


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
                 ):
        self.major_block = major_block
        self.minor_block = minor_block


class PrintablesFactory:
    def __init__(self, settings: LayoutSettings):
        self.settings = settings
        self.line_object_handler = _LineObjectHandler(self)

    @staticmethod
    def _blocks(settings: BlockSettings,
                parts: Sequence[Printable]) -> Printable:
        return ps.InterspersedSequencePrintable(
            settings.separator,
            parts
        )

    @staticmethod
    def _block(properties: BlockProperties,
               settings: BlockSettings,
               contents: Printable) -> Printable:
        ret_val = contents
        if properties.indented:
            ret_val = ps.IncreasedIndentPrintable(settings.indent,
                                                  ret_val)

        if properties.color is not None:
            ret_val = ps.ColoredPrintable(properties.color,
                                          ret_val)

        return ret_val

    def major_blocks(self,
                     blocks: Sequence[MajorBlock]) -> Printable:
        return self._blocks(
            self.settings.major_block,
            [
                self.major_block(block)
                for block in blocks
            ]
        )

    def minor_blocks(self,
                     blocks: Sequence[MinorBlock]) -> Printable:
        return self._blocks(
            self.settings.minor_block,
            [
                self.minor_block(block)
                for block in blocks
            ]
        )

    def major_block(self,
                    block: MajorBlock) -> Printable:
        contents = ps.SequencePrintable([self.minor_block(minor_block)
                                         for minor_block in block.parts])
        return self._block(block.properties,
                           self.settings.major_block,
                           contents
                           )

    def minor_block(self,
                    block: MinorBlock) -> Printable:
        contents = ps.SequencePrintable([
            _LineObjectPrintable(self.line_object_handler, line_object)
            for line_object in block.parts
        ])
        return self._block(block.properties,
                           self.settings.minor_block,
                           contents
                           )


class _LineObjectHandler(LineObjectVisitor[Printer, None]):
    def __init__(self, factory: PrintablesFactory):
        self._factory = factory

    def visit_pre_formatted(self, env: Printer, x: PreFormattedStringLineObject) -> None:
        env.write_indented(x.string)
        if not x.is_new_line_ended:
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
