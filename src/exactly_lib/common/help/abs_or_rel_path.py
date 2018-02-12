from typing import List

from exactly_lib.common.help.documentation_text import paths_uses_posix_syntax
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


def abs_or_rel_path_of_existing(file_type: str,
                                syntax_element: str,
                                relativity_root: str) -> List[ParagraphItem]:
    tp = TextParser({
        'file_type': file_type,
        'syntax_element': syntax_element,
        'relativity_root': relativity_root
    })
    return tp.fnap(_PATH_DESCRIPTION) + paths_uses_posix_syntax()


_PATH_DESCRIPTION = """\
The absolute or relative path of an existing {file_type}.


If {syntax_element} is relative, then it's relative to the {relativity_root}.
"""
