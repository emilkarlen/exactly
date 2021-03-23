from typing import List

from exactly_lib.definitions import formatting
from exactly_lib.definitions.test_case import reserved_words
from exactly_lib.section_document import defs
from exactly_lib.type_val_deps.types.list_ import defs as _list_defs
from exactly_lib.util.str_.name import NameWithGenderWithFormatting
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


def list_syntax_description(list_type: NameWithGenderWithFormatting) -> List[ParagraphItem]:
    tp = TextParser({
        'list_type': list_type,
        'r_paren': formatting.keyword(reserved_words.PAREN_END),
        'line_continuation': formatting.keyword(_list_defs.CONTINUATION_TOKEN),
        'end_of_line': defs.END_OF_LINE,
    })

    return tp.fnap(_DESCRIPTION)


_DESCRIPTION = """\
{list_type:a/u} continues until {end_of_line} or an unquoted {r_paren}.


An unquoted {line_continuation} at {end_of_line} makes the {list_type}
continue on the next line.
"""
