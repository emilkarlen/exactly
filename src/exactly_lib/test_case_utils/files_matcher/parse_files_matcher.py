from typing import Sequence

from exactly_lib.definitions import matcher_model
from exactly_lib.definitions.entity import syntax_elements, types
from exactly_lib.section_document import parser_classes
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.test_case_utils.expression import grammar
from exactly_lib.test_case_utils.expression import parser as ep
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher
from exactly_lib.test_case_utils.files_condition import parse as parse_fc
from exactly_lib.test_case_utils.files_matcher import config
from exactly_lib.test_case_utils.files_matcher import documentation
from exactly_lib.test_case_utils.files_matcher.impl import emptiness, num_files, quant_over_files, \
    sub_set_selection, prune
from exactly_lib.test_case_utils.files_matcher.impl.matches import matches_non_full, matches_full
from exactly_lib.test_case_utils.matcher import standard_expression_grammar
from exactly_lib.test_case_utils.matcher.impls import parse_quantified_matcher
from exactly_lib.type_system.logic.files_matcher import FilesMatcherSdv
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.logic_types import Quantifier
from exactly_lib.util.name_and_value import NameAndValue


def files_matcher_parser() -> Parser[FilesMatcherSdv]:
    return parser_classes.ParserFromTokenParserFunction(parse_files_matcher,
                                                        consume_last_line_if_is_at_eol_after_parse=True)


def parse_files_matcher(parser: TokenParser,
                        must_be_on_current_line: bool = True) -> FilesMatcherSdv:
    return ep.parse(GRAMMAR, parser, must_be_on_current_line)


def _file_quantified_assertion(quantifier: Quantifier,
                               parser: TokenParser) -> FilesMatcherSdv:
    return parse_quantified_matcher.parse_after_quantifier_token(
        quantifier,
        parse_file_matcher.ParserOfMatcherOnArbitraryLine(),
        quant_over_files.ELEMENT_SETUP,
        parser,
    )


def _parse_empty_check(parser: TokenParser) -> FilesMatcherSdv:
    return emptiness.emptiness_matcher()


def _parse_num_files_check(parser: TokenParser) -> FilesMatcherSdv:
    return num_files.parse(parser)


def _parse_selection(parser: TokenParser) -> FilesMatcherSdv:
    element_matcher = parse_file_matcher.parse_sdv(parser, False)
    matcher_on_selection = parse_files_matcher(parser, False)

    return sub_set_selection.matcher(element_matcher,
                                     matcher_on_selection)


def _parse_prune(parser: TokenParser) -> FilesMatcherSdv:
    element_matcher = parse_file_matcher.parse_sdv(parser, False)
    matcher_on_selection = parse_files_matcher(parser, False)

    return prune.matcher(element_matcher,
                         matcher_on_selection)


def _parse_matches(parser: TokenParser) -> FilesMatcherSdv:
    is_full = parser.consume_optional_option(config.MATCHES_FULL_OPTION.name)
    fc = parse_fc.parse(parser, False)
    return (
        matches_full.sdv(fc)
        if is_full
        else matches_non_full.sdv(fc)
    )


def _simple_expressions() -> Sequence[NameAndValue[grammar.PrimitiveExpression[FilesMatcherSdv]]]:
    ret_val = [
        NameAndValue(
            config.EMPTINESS_CHECK_ARGUMENT,
            grammar.PrimitiveExpression(_parse_empty_check,
                                        documentation.EmptyDoc())
        ),
        NameAndValue(
            config.MATCHES_ARGUMENT,
            grammar.PrimitiveExpression(_parse_matches,
                                        documentation.MatchesDoc())
        ),
    ]
    quantification_setup = parse_quantified_matcher.GrammarSetup(
        quant_over_files.ELEMENT_SETUP,
        parse_file_matcher.ParserOfMatcherOnArbitraryLine(),
    )

    ret_val += quantification_setup.quantification_grammar_expressions()

    ret_val += [
        NameAndValue(
            config.NUM_FILES_CHECK_ARGUMENT,
            grammar.PrimitiveExpression(_parse_num_files_check,
                                        documentation.NumFilesDoc())
        ),
        NameAndValue(
            option_syntax.option_syntax(config.SELECTION_OPTION.name),
            grammar.PrimitiveExpression(_parse_selection,
                                        documentation.SelectionDoc())
        ),
        NameAndValue(
            option_syntax.option_syntax(config.PRUNE_OPTION.name),
            grammar.PrimitiveExpression(_parse_prune,
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
)
