from typing import Sequence

from exactly_lib.definitions import matcher_model
from exactly_lib.definitions.entity import syntax_elements, types
from exactly_lib.definitions.primitives import files_matcher as files_matcher_primitives
from exactly_lib.section_document import parser_classes
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.files_matcher import FilesMatcherSdv
from exactly_lib.test_case_utils.expression import grammar
from exactly_lib.test_case_utils.expression import parser as ep
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher
from exactly_lib.test_case_utils.files_matcher import config
from exactly_lib.test_case_utils.files_matcher import documentation
from exactly_lib.test_case_utils.files_matcher.impl import emptiness, num_files, quant_over_files, \
    sub_set_selection, prune
from exactly_lib.test_case_utils.matcher import standard_expression_grammar
from exactly_lib.test_case_utils.matcher.impls import parse_quantified_matcher
from exactly_lib.type_system.logic.files_matcher import GenericFilesMatcherSdv
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.logic_types import Quantifier, ExpectationType
from exactly_lib.util.name_and_value import NameAndValue


def files_matcher_parser() -> Parser[FilesMatcherSdv]:
    return parser_classes.ParserFromTokenParserFunction(parse_files_matcher,
                                                        consume_last_line_if_is_at_eol_after_parse=True)


def parse_files_matcher(parser: TokenParser,
                        must_be_on_current_line: bool = True) -> FilesMatcherSdv:
    return FilesMatcherSdv(parse_files_matcher__generic(parser, must_be_on_current_line))


def parse_files_matcher__generic(parser: TokenParser,
                                 must_be_on_current_line: bool = True) -> GenericFilesMatcherSdv:
    return ep.parse(GRAMMAR, parser, must_be_on_current_line)


def _file_quantified_assertion(quantifier: Quantifier,
                               parser: TokenParser) -> GenericFilesMatcherSdv:
    return parse_quantified_matcher.parse_after_quantifier_token(
        quantifier,
        parse_file_matcher.ParserOfGenericMatcherOnArbitraryLine(),
        quant_over_files.ELEMENT_SETUP,
        parser,
    )


def _parse_empty_check(parser: TokenParser) -> GenericFilesMatcherSdv:
    return emptiness.emptiness_matcher__generic()


def _parse_num_files_check(parser: TokenParser) -> GenericFilesMatcherSdv:
    return num_files.parse__generic(ExpectationType.POSITIVE, parser)


def _parse_selection(parser: TokenParser) -> GenericFilesMatcherSdv:
    element_matcher = parse_file_matcher.parse_sdv(parser, False)
    matcher_on_selection = parse_files_matcher__generic(parser, False)

    return sub_set_selection.matcher(element_matcher,
                                     matcher_on_selection)


def _parse_prune(parser: TokenParser) -> GenericFilesMatcherSdv:
    element_matcher = parse_file_matcher.parse_sdv(parser, False)
    matcher_on_selection = parse_files_matcher__generic(parser, False)

    return prune.matcher(element_matcher,
                         matcher_on_selection)


def _simple_expressions() -> Sequence[NameAndValue[grammar.SimpleExpression[GenericFilesMatcherSdv]]]:
    ret_val = [
        NameAndValue(
            files_matcher_primitives.EMPTINESS_CHECK_ARGUMENT,
            grammar.SimpleExpression(_parse_empty_check,
                                     documentation.EmptyDoc())
        ),
    ]
    quantification_setup = parse_quantified_matcher.GrammarSetup(
        quant_over_files.ELEMENT_SETUP,
        parse_file_matcher.ParserOfGenericMatcherOnArbitraryLine(),
    )

    ret_val += quantification_setup.quantification_grammar_expressions()

    ret_val += [
        NameAndValue(
            files_matcher_primitives.NUM_FILES_CHECK_ARGUMENT,
            grammar.SimpleExpression(_parse_num_files_check,
                                     documentation.NumFilesDoc())
        ),
        NameAndValue(
            option_syntax.option_syntax(config.SELECTION_OPTION.name),
            grammar.SimpleExpression(_parse_selection,
                                     documentation.SelectionDoc())
        ),
        NameAndValue(
            option_syntax.option_syntax(config.PRUNE_OPTION.name),
            grammar.SimpleExpression(_parse_prune,
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
