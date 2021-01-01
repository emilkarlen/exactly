from typing import Sequence

from exactly_lib.common.help import headers
from exactly_lib.definitions import matcher_model
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.entity import types
from exactly_lib.definitions.primitives import line_matcher
from exactly_lib.impls import texts
from exactly_lib.impls.types.expression import grammar, parser as ep
from exactly_lib.impls.types.expression.parser import GrammarParsers
from exactly_lib.impls.types.line_matcher.impl import line_number
from exactly_lib.impls.types.line_matcher.impl.contents import parse as contents_parse, doc as contents_doc
from exactly_lib.impls.types.matcher import standard_expression_grammar
from exactly_lib.impls.types.matcher.impls import combinator_matchers
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.type_val_deps.types.line_matcher import LineMatcherSdv
from exactly_lib.type_val_prims.matcher.line_matcher import FIRST_LINE_NUMBER_DESCRIPTION
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


def parsers(must_be_on_current_line: bool = False) -> GrammarParsers[LineMatcherSdv]:
    return _PARSERS_FOR_MUST_BE_ON_CURRENT_LINE[must_be_on_current_line]


_TP = TextParser({
    'INTEGER_MATCHER': syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT.singular_name,
    'MODEL': matcher_model.LINE_MATCHER_MODEL,
    'FIRST_LINE_NUMBER_DESCRIPTION': FIRST_LINE_NUMBER_DESCRIPTION,
    'Note': headers.NOTE_LINE_HEADER,
})

_LINE_NUMBER_MATCHER_SED_DESCRIPTION = """\
Matches {MODEL:s} who's line number matches {INTEGER_MATCHER}.


{Note} {FIRST_LINE_NUMBER_DESCRIPTION}
"""


class _LineNumberSyntaxDescription(grammar.PrimitiveDescriptionWithNameAsInitialSyntaxToken):
    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return [
            syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT.single_mandatory,
        ]

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return (
                _TP.fnap(_LINE_NUMBER_MATCHER_SED_DESCRIPTION) +
                texts.type_expression_has_syntax_of_primitive([
                    syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT.singular_name,
                ])
        )

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return [syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT.cross_reference_target]


_CONCEPT = grammar.Concept(
    types.LINE_MATCHER_TYPE_INFO.name,
    types.LINE_MATCHER_TYPE_INFO.identifier,
    syntax_elements.LINE_MATCHER_SYNTAX_ELEMENT.argument,
)

GRAMMAR = standard_expression_grammar.new_grammar(
    _CONCEPT,
    model=matcher_model.LINE_MATCHER_MODEL,
    value_type=ValueType.LINE_MATCHER,
    simple_expressions=(
        NameAndValue(
            line_matcher.CONTENTS_MATCHER_NAME,
            grammar.Primitive(contents_parse.PARSER.parse,
                              contents_doc.SyntaxDescription())
        ),
        NameAndValue(
            line_matcher.LINE_NUMBER_MATCHER_NAME,
            grammar.Primitive(line_number.parse_line_number,
                              _LineNumberSyntaxDescription())
        ),
    ),
    model_freezer=combinator_matchers.no_op_freezer,
)

_PARSERS_FOR_MUST_BE_ON_CURRENT_LINE = ep.parsers_for_must_be_on_current_line(GRAMMAR)
