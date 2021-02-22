from typing import Sequence

from exactly_lib.definitions import matcher_model
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.entity import types
from exactly_lib.definitions.primitives import string_transformer
from exactly_lib.impls import texts
from exactly_lib.impls.types.expression import grammar
from exactly_lib.impls.types.expression import parser as ep
from exactly_lib.impls.types.expression.descriptions import alias
from exactly_lib.impls.types.expression.parser import GrammarParsers
from exactly_lib.impls.types.line_matcher import parse_line_matcher
from exactly_lib.impls.types.matcher import standard_expression_grammar
from exactly_lib.impls.types.matcher.impls import parse_quantified_matcher
from exactly_lib.impls.types.string_matcher import matcher_options
from exactly_lib.impls.types.string_matcher.impl import on_transformed
from exactly_lib.impls.types.string_matcher.parse import emptieness, equality, line_matches, matches, num_lines, \
    run_program
from exactly_lib.impls.types.string_transformer import parse_string_transformer
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.type_val_deps.types.string_matcher import StringMatcherSdv
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


def parsers(must_be_on_current_line: bool = False) -> GrammarParsers[StringMatcherSdv]:
    return _PARSERS_FOR_MUST_BE_ON_CURRENT_LINE[must_be_on_current_line]


def _parse_on_transformed(parser: TokenParser) -> StringMatcherSdv:
    transformer = _STRING_TRANSFORMER_PARSER.parse_from_token_parser(parser)
    matcher_on_transformed = _STRING_MATCHER_COMPONENT_PARSER.parse_from_token_parser(parser)
    return on_transformed.StringMatcherWithTransformationSdv(transformer, matcher_on_transformed)


class _OnTransformedDescription(grammar.PrimitiveDescriptionWithNameAsInitialSyntaxToken):
    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return (
            syntax_elements.STRING_TRANSFORMER_SYNTAX_ELEMENT.single_mandatory,
            syntax_elements.STRING_MATCHER_SYNTAX_ELEMENT.single_mandatory,
        )

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        tp = TextParser({
            'MATCHER': syntax_elements.STRING_MATCHER_SYNTAX_ELEMENT.singular_name,
            'TRANSFORMER': syntax_elements.STRING_TRANSFORMER_SYNTAX_ELEMENT.singular_name,
            'MODEL': matcher_model.TEXT_MODEL,
        })
        ret_val = tp.fnap(_DESCRIPTION__ON_TRANSFORMED)
        ret_val += texts.type_expression_has_syntax_of_primitive([
            syntax_elements.STRING_TRANSFORMER_SYNTAX_ELEMENT.singular_name,
            syntax_elements.STRING_MATCHER_SYNTAX_ELEMENT.singular_name,
        ])
        return ret_val

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return syntax_elements.STRING_TRANSFORMER_SYNTAX_ELEMENT.cross_reference_target,


def _simple_expressions() -> Sequence[NameAndValue[grammar.Primitive[StringMatcherSdv]]]:
    equals_entry = NameAndValue(
        matcher_options.EQUALS_ARGUMENT,
        grammar.Primitive(equality.EqualsParser().parse_from_token_parser,
                          equality.Description())
    )
    matches_entry = NameAndValue(
        matcher_options.MATCHES_ARGUMENT,
        grammar.Primitive(matches.parse,
                          matches.Description())
    )

    ret_val = [
        NameAndValue(
            matcher_options.EMPTY_ARGUMENT,
            grammar.Primitive(emptieness.parse,
                              emptieness.Description())
        ),
        equals_entry,
        alias.entry(matcher_options.EQUALS_ARGUMENT__ALTERNATIVE,
                    equals_entry),
        matches_entry,
        alias.entry(matcher_options.MATCHES_ARGUMENT__ALTERNATIVE,
                    matches_entry),
    ]

    quantification_setup = parse_quantified_matcher.GrammarSetup(
        line_matches.line_matchers.ELEMENT_SETUP,
        parse_line_matcher.parsers().simple,
    )

    ret_val += quantification_setup.quantification_grammar_expressions()

    ret_val += [
        NameAndValue(
            matcher_options.NUM_LINES_ARGUMENT,
            grammar.Primitive(num_lines.parse,
                              num_lines.Description())
        ),
        NameAndValue(
            matcher_options.RUN_PROGRAM_ARGUMENT,
            grammar.Primitive(
                run_program.parse,
                run_program.SyntaxDescription(),
            )
        ),
        NameAndValue(
            option_syntax.option_syntax(
                string_transformer.WITH_TRANSFORMED_CONTENTS_OPTION_NAME),
            grammar.Primitive(_parse_on_transformed,
                              _OnTransformedDescription())
        ),
    ]

    return ret_val


def _model_freezer(model: StringSource) -> StringSource:
    model.freeze()
    return model


GRAMMAR = standard_expression_grammar.new_grammar(
    concept=grammar.Concept(
        name=types.STRING_MATCHER_TYPE_INFO.name,
        type_system_type_name=types.STRING_MATCHER_TYPE_INFO.identifier,
        syntax_element_name=syntax_elements.STRING_MATCHER_SYNTAX_ELEMENT.argument,
    ),
    model=matcher_model.TEXT_MODEL,
    value_type=ValueType.STRING_MATCHER,
    simple_expressions=_simple_expressions(),
    model_freezer=_model_freezer,
)

_PARSERS_FOR_MUST_BE_ON_CURRENT_LINE = ep.parsers_for_must_be_on_current_line(GRAMMAR)

_STRING_TRANSFORMER_PARSER = parse_string_transformer.parsers().simple
_STRING_MATCHER_COMPONENT_PARSER = parsers().simple

_DESCRIPTION__ON_TRANSFORMED = """\
Applies {MATCHER} to the original {MODEL} transformed by {TRANSFORMER}.
"""
