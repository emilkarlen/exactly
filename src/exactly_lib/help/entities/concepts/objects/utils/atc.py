from typing import Sequence

from exactly_lib.definitions import formatting, misc_texts
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


def atc_examples() -> Sequence[ParagraphItem]:
    return [
        docs.simple_header_only_list([
            _TP.text(example)
            for example in _EXAMPLES
        ],
            lists.ListType.ITEMIZED_LIST,
        )
    ]


_EXAMPLES = [
    'executable program file (with arguments)',
    'source code file (with arguments)',
    'source code',
    '{shell_command}',
]

_TP = TextParser({
    'shell_command': formatting.misc_name_with_formatting(misc_texts.SHELL_COMMAND_LINE),
})
