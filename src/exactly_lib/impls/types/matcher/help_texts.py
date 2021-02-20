from typing import List

from exactly_lib.common.help import headers
from exactly_lib.definitions import misc_texts
from exactly_lib.definitions.entity import types, syntax_elements
from exactly_lib.impls.types.program.help_texts import TRANSFORMATION_ARE_IGNORED__TMPL
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


def run_program_matcher_description(exe_env: List[ParagraphItem]) -> List[ParagraphItem]:
    tp = TextParser({
        'program': types.PROGRAM_TYPE_INFO.name,
        'PROGRAM': syntax_elements.PROGRAM_SYNTAX_ELEMENT.singular_name,
        'exit_code': misc_texts.EXIT_CODE,
        'Note': headers.NOTE_LINE_HEADER,
    })
    return (
            tp.fnap(_HEADER) +
            exe_env +
            tp.fnap(TRANSFORMATION_ARE_IGNORED__TMPL)
    )


_HEADER = """\
Runs {program:a}, and matches iff its {exit_code} is 0.
"""
