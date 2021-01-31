from typing import Sequence

from exactly_lib.definitions import formatting
from exactly_lib.impls.types.expression import grammar
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


class Description(grammar.PrimitiveDescriptionWithNameAsInitialSyntaxToken):
    def __init__(self,
                 aliased: str,
                 arguments: Sequence[a.ArgumentUsage],
                 ):
        self._aliased = aliased
        self._arguments = arguments

    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return self._arguments

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        tp = TextParser({
            'aliased': formatting.keyword(self._aliased),
        })
        return tp.fnap(_DESCRIPTION)


_DESCRIPTION = """\
An alias for {aliased}.
"""
