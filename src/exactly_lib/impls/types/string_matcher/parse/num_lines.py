from typing import Sequence

from exactly_lib.definitions import matcher_model
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.impls import texts
from exactly_lib.impls.types.expression import grammar
from exactly_lib.impls.types.integer_matcher import parse_integer_matcher
from exactly_lib.impls.types.string_matcher.impl import num_lines
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.type_val_deps.types.string_matcher import StringMatcherSdv
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


def parse(token_parser: TokenParser) -> StringMatcherSdv:
    matcher = _MATCHER_PARSER.parse_from_token_parser(token_parser)
    return num_lines.sdv(matcher)


_MATCHER_PARSER = parse_integer_matcher.parsers().simple


class Description(grammar.PrimitiveDescriptionWithNameAsInitialSyntaxToken):
    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT.single_mandatory,

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        tp = TextParser({
            'INTEGER_MATCHER': syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT.singular_name,
            'model': matcher_model.TEXT_MODEL,
            'line_model': matcher_model.LINE_MATCHER_MODEL,
        })
        return (
                tp.fnap(_DESCRIPTION) +
                texts.type_expression_has_syntax_of_primitive([
                    syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT.singular_name,
                ])
        )

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT.cross_reference_target,


_DESCRIPTION = """\
Matches iff the number of {line_model:s} of the {model} matches {INTEGER_MATCHER}.
"""
