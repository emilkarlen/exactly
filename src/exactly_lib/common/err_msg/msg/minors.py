from typing import Any, Optional

from exactly_lib.common.report_rendering.text_doc import MinorTextRenderer
from exactly_lib.definitions import misc_texts
from exactly_lib.util.file_printer import FilePrintable
from exactly_lib.util.name import Name
from exactly_lib.util.simple_textstruct import structure
from exactly_lib.util.simple_textstruct.rendering import renderer_combinators as rend_comb, blocks, line_objects, \
    component_renderers as comp_rend, strings, line_elements, renderer_combinators as rend_comp
from exactly_lib.util.simple_textstruct.rendering.renderer import SequenceRenderer
from exactly_lib.util.simple_textstruct.structure import LineElement


def _capitalize_singular(x: Name) -> str:
    return x.singular.capitalize()


def single_pre_formatted(s: str) -> MinorTextRenderer:
    return rend_comb.SingletonSequenceR(
        comp_rend.MinorBlockR(line_elements.single_pre_formatted(s))
    )


def header_and_message(single_line_header: Any,
                       message: SequenceRenderer[LineElement]) -> MinorTextRenderer:
    return rend_comb.SequenceR([
        blocks.MinorBlockOfSingleLineObject(
            line_objects.StringLineObject(single_line_header),
        ),
        comp_rend.MinorBlockR(message),
    ])


def category_error_message(category: Name,
                           message: SequenceRenderer[LineElement]) -> MinorTextRenderer:
    return header_and_message(strings.Transformed(category, _capitalize_singular),
                              message)


def syntax_error_message(message: SequenceRenderer[LineElement]) -> MinorTextRenderer:
    return category_error_message(misc_texts.SYNTAX_ERROR_NAME, message)


def file_access_error_message(message: SequenceRenderer[LineElement]) -> MinorTextRenderer:
    return category_error_message(misc_texts.FILE_ACCESS_ERROR_NAME,
                                  message)


def of_file_printable(fp: FilePrintable,
                      is_line_ended: bool = False) -> MinorTextRenderer:
    return blocks.MinorBlocksOfSingleLineObject(
        rend_comp.ConstantR(structure.FilePrintableLineObject(fp, is_line_ended))
    )


def of_file_printable__opt(fp: Optional[FilePrintable],
                           is_line_ended: bool = False) -> Optional[MinorTextRenderer]:
    return (
        None
        if fp is None
        else blocks.MinorBlocksOfSingleLineObject(
            rend_comp.ConstantR(structure.FilePrintableLineObject(fp, is_line_ended))
        ))
