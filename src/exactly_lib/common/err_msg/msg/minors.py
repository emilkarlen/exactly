from typing import Any

from exactly_lib.common.report_rendering.text_doc import MinorTextRenderer
from exactly_lib.definitions import misc_texts
from exactly_lib.util import strings
from exactly_lib.util.name import Name
from exactly_lib.util.render import combinators as rend_comb
from exactly_lib.util.render.renderer import SequenceRenderer
from exactly_lib.util.simple_textstruct.rendering import blocks, line_objects, \
    component_renderers as comp_rend, line_elements
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
