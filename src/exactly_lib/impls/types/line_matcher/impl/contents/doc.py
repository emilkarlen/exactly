from typing import Sequence

from exactly_lib.definitions import matcher_model
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.impls.types.expression import grammar
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser

_TP = TextParser({
    'MODEL': matcher_model.LINE_MATCHER_MODEL,
    'STRING_MATCHER': syntax_elements.STRING_MATCHER_SYNTAX_ELEMENT.singular_name,
})


class SyntaxDescription(grammar.PrimitiveDescriptionWithNameAsInitialSyntaxToken):
    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return [
            syntax_elements.STRING_MATCHER_SYNTAX_ELEMENT.single_mandatory,
        ]

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return _TP.fnap(_DESCRIPTION)

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return [syntax_elements.STRING_MATCHER_SYNTAX_ELEMENT.cross_reference_target]


_DESCRIPTION = """\
Matches {MODEL:s} who's text contents matches {STRING_MATCHER}.
"""
