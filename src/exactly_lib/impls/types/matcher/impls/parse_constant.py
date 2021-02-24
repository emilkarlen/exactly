from typing import Sequence

from exactly_lib.definitions import logic
from exactly_lib.impls.types.expression import grammar
from exactly_lib.impls.types.matcher.impls import sdv_components, constant
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.type_val_deps.types.matcher import MatcherSdv
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


def parse_constant(parser: TokenParser) -> MatcherSdv:
    return parser.consume_mandatory_constant_string_that_must_be_unquoted_and_equal(
        logic.BOOLEANS_STRINGS.keys(),
        _make_constant_matcher,
    )


def _make_constant_matcher(boolean_keyword: str) -> MatcherSdv:
    return sdv_components.matcher_sdv_from_constant_primitive(
        constant.MatcherWithConstantResult(logic.BOOLEANS_STRINGS[boolean_keyword])
    )


class _Description(grammar.PrimitiveDescriptionWithNameAsInitialSyntaxToken):
    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return [
            a.Choice.of_single_argument_choices(
                a.Multiplicity.MANDATORY,
                [a.Named(value) for value in logic.BOOLEANS.values()]
            )
        ]

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return _TP.fnap(_DESCRIPTION)


CONSTANT_PRIMITIVE = NameAndValue(
    logic.CONSTANT_MATCHER,
    grammar.Primitive(
        parse_constant,
        _Description()
    )
)

_TP = TextParser({
    'false': logic.BOOLEANS[False],
    'true': logic.BOOLEANS[True],
})

_DESCRIPTION = """\
Unconditionally {false} or {true}.
"""
