from typing import List

from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem

POSIX_SYNTAX = 'Posix syntax'


def paths_uses_posix_syntax() -> List[ParagraphItem]:
    return docs.paras('Paths uses ' + POSIX_SYNTAX + '.')
