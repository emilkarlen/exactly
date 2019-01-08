from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.entity import syntax_elements, concepts
from exactly_lib.section_document import parser_classes
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol import symbol_syntax
from exactly_lib.symbol.files_matcher import FilesMatcherResolver
from exactly_lib.symbol.resolver_structure import StringMatcherResolver
from exactly_lib.test_case_utils.condition.integer import parse_integer_condition as expression_parse
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher
from exactly_lib.test_case_utils.files_matcher import config
from exactly_lib.test_case_utils.files_matcher.impl import emptiness, num_files, quant_over_files, sub_set_selection, \
    negation
from exactly_lib.test_case_utils.files_matcher.impl import symbol_reference
from exactly_lib.test_case_utils.string_matcher.parse import parse_string_matcher
from exactly_lib.util.logic_types import Quantifier, ExpectationType


def files_matcher_parser() -> Parser[FilesMatcherResolver]:
    return parser_classes.ParserFromTokenParserFunction(parse_files_matcher)


def parse_files_matcher(parser: TokenParser,
                        must_be_on_current_line: bool = True) -> FilesMatcherResolver:
    if must_be_on_current_line:
        parser.require_is_not_at_eol('Missing ' + syntax_elements.FILES_MATCHER_SYNTAX_ELEMENT.singular_name)

    mb_file_selector = parse_file_matcher.parse_optional_selection_resolver2(parser)
    expectation_type = parser.consume_optional_negation_operator()

    ret_val = _SIMPLE_MATCHER_PARSER.parse(parser)

    if expectation_type is ExpectationType.NEGATIVE:
        ret_val = negation.negation_matcher(ret_val)

    if mb_file_selector is not None:
        ret_val = sub_set_selection.sub_set_selection_matcher(mb_file_selector,
                                                              ret_val)

    return ret_val


class _SimpleMatcherParser:
    def __init__(self):
        self.matcher_parsers = {
            config.NUM_FILES_CHECK_ARGUMENT: self.parse_num_files_check,
            config.EMPTINESS_CHECK_ARGUMENT: self.parse_empty_check,
            instruction_arguments.ALL_QUANTIFIER_ARGUMENT: self.parse_file_quantified_assertion__all,
            instruction_arguments.EXISTS_QUANTIFIER_ARGUMENT: self.parse_file_quantified_assertion__exists,
        }

    def parse(self, parser: TokenParser) -> FilesMatcherResolver:
        matcher_name = parser.consume_mandatory_unquoted_string(
            syntax_elements.FILES_MATCHER_SYNTAX_ELEMENT.singular_name,
            False)
        if matcher_name in self.matcher_parsers:
            return self.matcher_parsers[matcher_name](parser)
        else:
            return self.parse_symbol_reference(matcher_name, parser)

    def parse_empty_check(self, parser: TokenParser) -> FilesMatcherResolver:
        self._expect_no_more_args_and_consume_current_line(parser)
        return emptiness.emptiness_matcher(ExpectationType.POSITIVE)

    def parse_num_files_check(self, parser: TokenParser) -> FilesMatcherResolver:
        cmp_op_and_rhs = expression_parse.parse_integer_comparison_operator_and_rhs(
            parser,
            expression_parse.validator_for_non_negative)

        self._expect_no_more_args_and_consume_current_line(parser)

        return num_files.num_files_matcher(ExpectationType.POSITIVE, cmp_op_and_rhs)

    def parse_file_quantified_assertion__all(self, parser: TokenParser) -> FilesMatcherResolver:
        return self._file_quantified_assertion(Quantifier.ALL, parser)

    def parse_file_quantified_assertion__exists(self, parser: TokenParser) -> FilesMatcherResolver:
        return self._file_quantified_assertion(Quantifier.EXISTS, parser)

    def parse_symbol_reference(self, parsed_symbol_name: str, parser: TokenParser) -> FilesMatcherResolver:
        if symbol_syntax.is_symbol_name(parsed_symbol_name):
            self._expect_no_more_args_and_consume_current_line(parser)
            return symbol_reference.symbol_reference_matcher(parsed_symbol_name)
        else:
            err_msg_header = 'Neither a {matcher} nor the plain name of a {symbol}: '.format(
                matcher=syntax_elements.FILES_MATCHER_SYNTAX_ELEMENT.singular_name,
                symbol=concepts.SYMBOL_CONCEPT_INFO.singular_name)
            raise SingleInstructionInvalidArgumentException(err_msg_header + parsed_symbol_name)

    def _file_quantified_assertion(self,
                                   quantifier: Quantifier,
                                   parser: TokenParser) -> FilesMatcherResolver:
        parser.consume_mandatory_constant_unquoted_string(config.QUANTIFICATION_OVER_FILE_ARGUMENT,
                                                          must_be_on_current_line=True)
        parser.consume_mandatory_constant_unquoted_string(
            instruction_arguments.QUANTIFICATION_SEPARATOR_ARGUMENT,
            must_be_on_current_line=True)
        matcher_on_existing_regular_file = parse_string_matcher.parse_string_matcher(parser)

        return self._file_quantified_assertion_part(quantifier,
                                                    matcher_on_existing_regular_file)

    def _file_quantified_assertion_part(self,
                                        quantifier: Quantifier,
                                        matcher_on_existing_regular_file: StringMatcherResolver,
                                        ) -> FilesMatcherResolver:
        return quant_over_files.quantified_matcher(ExpectationType.POSITIVE,
                                                   quantifier,
                                                   matcher_on_existing_regular_file)

    @staticmethod
    def _expect_no_more_args_and_consume_current_line(parser: TokenParser):
        parser.report_superfluous_arguments_if_not_at_eol()
        parser.consume_current_line_as_string_of_remaining_part_of_current_line()


_SIMPLE_MATCHER_PARSER = _SimpleMatcherParser()
