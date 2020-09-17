from typing import List

from exactly_lib.cli.definitions import exit_codes
from exactly_lib.definitions import misc_texts
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


def paragraphs() -> List[ParagraphItem]:
    tp = TextParser({
        'exit_code': misc_texts.EXIT_CODE,
        'INVALID_USAGE': exit_codes.EXIT_INVALID_USAGE,
    })
    return tp.fnap(_DESCRIPTION)


_DESCRIPTION = """
Invalid command line arguments: Exit with {exit_code} {INVALID_USAGE}.
"""
