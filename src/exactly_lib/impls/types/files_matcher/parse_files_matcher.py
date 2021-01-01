from typing import Sequence

from exactly_lib.definitions import matcher_model
from exactly_lib.definitions.entity import syntax_elements, types
from exactly_lib.impls.types.expression import grammar
from exactly_lib.impls.types.expression import parser as ep
from exactly_lib.impls.types.expression.parser import GrammarParsers
from exactly_lib.impls.types.file_matcher import parse_file_matcher
from exactly_lib.impls.types.files_condition import parse as parse_fc
from exactly_lib.impls.types.files_matcher import config
from exactly_lib.impls.types.files_matcher import documentation
from exactly_lib.impls.types.files_matcher.impl import emptiness, num_files, quant_over_files, \
    sub_set_selection, prune
from exactly_lib.impls.types.files_matcher.impl.matches import matches_non_full, matches_full
from exactly_lib.impls.types.matcher import standard_expression_grammar
from exactly_lib.impls.types.matcher.impls import parse_quantified_matcher, combinator_matchers
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.type_val_deps.types.files_matcher import FilesMatcherSdv
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.name_and_value import NameAndValue


def parsers(must_be_on_current_line: bool = False) -> GrammarParsers[FilesMatcherSdv]:
    return _PARSERS_FOR_MUST_BE_ON_CURRENT_LINE[must_be_on_current_line]


def _parse_empty_check(parser: TokenParser) -> FilesMatcherSdv:
    return emptiness.emptiness_matcher()


def _parse_selection(parser: TokenParser) -> FilesMatcherSdv:
    element_matcher = _FILE_MATCHER_COMPONENT_PARSER.parse_from_token_parser(parser)
    matcher_on_selection = _FILES_MATCHER_COMPONENT_PARSER.parse_from_token_parser(parser)

    return sub_set_selection.matcher(element_matcher,
                                     matcher_on_selection)


def _parse_prune(parser: TokenParser) -> FilesMatcherSdv:
    element_matcher = _FILE_MATCHER_COMPONENT_PARSER.parse_from_token_parser(parser)
    matcher_on_selection = _FILES_MATCHER_COMPONENT_PARSER.parse_from_token_parser(parser)

    return prune.matcher(element_matcher,
                         matcher_on_selection)


def _parse_matches(parser: TokenParser) -> FilesMatcherSdv:
    is_full = parser.consume_optional_option(config.MATCHES_FULL_OPTION.name)
    fc = _FILES_CONDITION_COMPONENT_PARSER.parse_from_token_parser(parser)
    return (
        matches_full.sdv(fc)
        if is_full
        else matches_non_full.sdv(fc)
    )


def _simple_expressions() -> Sequence[NameAndValue[grammar.Primitive[FilesMatcherSdv]]]:
    ret_val = [
        NameAndValue(
            config.EMPTINESS_CHECK_ARGUMENT,
            grammar.Primitive(_parse_empty_check,
                              documentation.EmptyDoc())
        ),
        NameAndValue(
            config.MATCHES_ARGUMENT,
            grammar.Primitive(_parse_matches,
                              documentation.MatchesDoc())
        ),
    ]
    quantification_setup = parse_quantified_matcher.GrammarSetup(
        quant_over_files.ELEMENT_SETUP,
        parse_file_matcher.parsers().simple,
    )

    ret_val += quantification_setup.quantification_grammar_expressions()

    ret_val += [
        NameAndValue(
            config.NUM_FILES_CHECK_ARGUMENT,
            grammar.Primitive(num_files.parser().parse,
                              documentation.NumFilesDoc())
        ),
        NameAndValue(
            option_syntax.option_syntax(config.SELECTION_OPTION.name),
            grammar.Primitive(_parse_selection,
                              documentation.SelectionDoc())
        ),
        NameAndValue(
            option_syntax.option_syntax(config.PRUNE_OPTION.name),
            grammar.Primitive(_parse_prune,
                              documentation.PruneDoc())
        ),
    ]
    return ret_val


GRAMMAR = standard_expression_grammar.new_grammar(
    concept=grammar.Concept(
        name=types.FILES_MATCHER_TYPE_INFO.name,
        type_system_type_name=types.FILES_MATCHER_TYPE_INFO.identifier,
        syntax_element_name=syntax_elements.FILES_MATCHER_SYNTAX_ELEMENT.argument,
    ),
    model=matcher_model.FILES_MATCHER_MODEL,
    value_type=ValueType.FILES_MATCHER,
    simple_expressions=_simple_expressions(),
    model_freezer=combinator_matchers.no_op_freezer,
)

_PARSERS_FOR_MUST_BE_ON_CURRENT_LINE = ep.parsers_for_must_be_on_current_line(GRAMMAR)

_FILES_MATCHER_COMPONENT_PARSER = parsers().simple

_FILE_MATCHER_COMPONENT_PARSER = parse_file_matcher.parsers().simple

_FILES_CONDITION_COMPONENT_PARSER = parse_fc.parsers().full
