import contextlib
from typing import Iterator, ContextManager

from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.line_matcher import LineMatcherResolver
from exactly_lib.symbol.logic.string_matcher import StringMatcherResolver
from exactly_lib.test_case.validation import pre_or_post_validation as ppv, pre_or_post_value_validation as ppvv
from exactly_lib.test_case_utils.line_matcher.model_construction import model_iter_from_file_line_iter
from exactly_lib.test_case_utils.line_matcher.parse_line_matcher import parse_line_matcher_from_token_parser
from exactly_lib.test_case_utils.line_matcher.trace_rendering import LineMatcherLineRenderer
from exactly_lib.test_case_utils.string_matcher import delegated_matcher, resolvers
from exactly_lib.test_case_utils.string_matcher import matcher_options
from exactly_lib.type_system.logic.impls import quantifier_matchers, combinator_matchers
from exactly_lib.type_system.logic.line_matcher import LineMatcherLine
from exactly_lib.type_system.logic.string_matcher import FileToCheck, StringMatcherValue
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable


def parse_any_line_matches_matcher(expectation_type: ExpectationType,
                                   token_parser: TokenParser) -> StringMatcherResolver:
    line_matcher_resolver = _parse_line_matches_tokens_and_line_matcher(token_parser)

    return matcher_for_any_line_matches(expectation_type,
                                        line_matcher_resolver)


def parse_every_line_matches_matcher(expectation_type: ExpectationType,
                                     token_parser: TokenParser) -> StringMatcherResolver:
    line_matcher_resolver = _parse_line_matches_tokens_and_line_matcher(token_parser)

    return matcher_for_every_line_matches(expectation_type,
                                          line_matcher_resolver)


def _parse_line_matches_tokens_and_line_matcher(token_parser: TokenParser) -> LineMatcherResolver:
    token_parser.consume_mandatory_constant_unquoted_string(matcher_options.LINE_ARGUMENT,
                                                            must_be_on_current_line=True)
    token_parser.consume_mandatory_constant_unquoted_string(instruction_arguments.QUANTIFICATION_SEPARATOR_ARGUMENT,
                                                            must_be_on_current_line=True)
    line_matcher_resolver = parse_line_matcher_from_token_parser(token_parser,
                                                                 must_be_on_current_line=False)

    return line_matcher_resolver


def matcher_for_any_line_matches(expectation_type: ExpectationType,
                                 line_matcher_resolver: LineMatcherResolver) -> StringMatcherResolver:
    def get_matcher(symbols: SymbolTable) -> StringMatcherValue:
        matcher = quantifier_matchers.ExistsValue(
            _element_setup(),
            line_matcher_resolver.resolve(symbols),
        )
        if expectation_type is ExpectationType.NEGATIVE:
            matcher = combinator_matchers.NegationValue(matcher)

        return delegated_matcher.StringMatcherValueDelegatedToMatcher(matcher)

    return resolvers.StringMatcherResolverFromParts2(
        line_matcher_resolver.references,
        _validator_for_line_matcher(line_matcher_resolver),
        get_matcher,
    )


def matcher_for_every_line_matches(expectation_type: ExpectationType,
                                   line_matcher_resolver: LineMatcherResolver) -> StringMatcherResolver:
    def get_matcher(symbols: SymbolTable) -> StringMatcherValue:
        matcher = quantifier_matchers.ForAllValue(
            _element_setup(),
            line_matcher_resolver.resolve(symbols),
        )
        if expectation_type is ExpectationType.NEGATIVE:
            matcher = combinator_matchers.NegationValue(matcher)

        return delegated_matcher.StringMatcherValueDelegatedToMatcher(matcher)

    return resolvers.StringMatcherResolverFromParts2(
        line_matcher_resolver.references,
        _validator_for_line_matcher(line_matcher_resolver),
        get_matcher,
    )


def _validator_for_line_matcher(line_matcher_resolver: LineMatcherResolver) -> ppv.PreOrPostSdsValidator:
    def get_validator(symbols: SymbolTable) -> ppvv.PreOrPostSdsValueValidator:
        return line_matcher_resolver.resolve(symbols).validator

    return ppv.PreOrPostSdsValidatorFromValueValidator(get_validator)


def _element_setup() -> quantifier_matchers.ElementSetup[FileToCheck, LineMatcherLine]:
    return quantifier_matchers.ElementSetup(
        matcher_options.LINE_ARGUMENT,
        syntax_elements.LINE_MATCHER_SYNTAX_ELEMENT.singular_name,
        _get_line_elements,
        _line_renderer,
    )


@contextlib.contextmanager
def _get_line_elements(string_matcher_model: FileToCheck) -> ContextManager[Iterator[LineMatcherLine]]:
    with string_matcher_model.lines() as lines:
        yield model_iter_from_file_line_iter(lines)


def _line_renderer(line: LineMatcherLine) -> DetailsRenderer:
    return LineMatcherLineRenderer(line)
