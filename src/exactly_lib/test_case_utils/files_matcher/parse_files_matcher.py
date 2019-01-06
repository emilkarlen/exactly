from exactly_lib.definitions import instruction_arguments
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.resolver_structure import StringMatcherResolver
from exactly_lib.test_case_utils.condition.integer import parse_integer_condition as expression_parse
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher
from exactly_lib.test_case_utils.files_matcher import files_matchers, config
from exactly_lib.test_case_utils.files_matcher.impl import emptiness, num_files, quant_over_files
from exactly_lib.test_case_utils.files_matcher.impl.sub_set_selection import sub_set_selection_matcher
from exactly_lib.test_case_utils.files_matcher.structure import FilesMatcherResolver
from exactly_lib.test_case_utils.string_matcher.parse import parse_string_matcher
from exactly_lib.util.logic_types import Quantifier
from exactly_lib.util.messages import grammar_options_syntax


def parse_files_matcher(parser: TokenParser) -> FilesMatcherResolver:
    mb_file_selector = parse_file_matcher.parse_optional_selection_resolver2(parser)
    expectation_type = parser.consume_optional_negation_operator()

    files_matcher_parser = _FilesMatcherParserForSettings(
        files_matchers.Settings(expectation_type,
                                None))
    matcher_without_selection = files_matcher_parser.parse(parser)

    if mb_file_selector is None:
        return matcher_without_selection
    else:
        return sub_set_selection_matcher(mb_file_selector,
                                         matcher_without_selection)


class _FilesMatcherParserForSettings:
    def __init__(self, settings: files_matchers.Settings):
        self.settings = settings
        self.command_parsers = {
            config.NUM_FILES_CHECK_ARGUMENT: self.parse_num_files_check,
            config.EMPTINESS_CHECK_ARGUMENT: self.parse_empty_check,
            instruction_arguments.ALL_QUANTIFIER_ARGUMENT: self.parse_file_quantified_assertion__all,
            instruction_arguments.EXISTS_QUANTIFIER_ARGUMENT: self.parse_file_quantified_assertion__exists,
        }
        self.missing_check_description = 'Missing argument for check :' + grammar_options_syntax.alternatives_list(
            self.command_parsers)

    def parse(self, parser: TokenParser) -> FilesMatcherResolver:
        return parser.parse_mandatory_command(self.command_parsers,
                                              self.missing_check_description)

    def parse_empty_check(self, parser: TokenParser) -> FilesMatcherResolver:
        self._expect_no_more_args_and_consume_current_line(parser)
        return emptiness.emptiness_matcher(self.settings)

    def parse_num_files_check(self, parser: TokenParser) -> FilesMatcherResolver:
        cmp_op_and_rhs = expression_parse.parse_integer_comparison_operator_and_rhs(
            parser,
            expression_parse.validator_for_non_negative)

        self._expect_no_more_args_and_consume_current_line(parser)

        return num_files.num_files_matcher(self.settings, cmp_op_and_rhs)

    def parse_file_quantified_assertion__all(self, parser: TokenParser) -> FilesMatcherResolver:
        return self._file_quantified_assertion(Quantifier.ALL, parser)

    def parse_file_quantified_assertion__exists(self, parser: TokenParser) -> FilesMatcherResolver:
        return self._file_quantified_assertion(Quantifier.EXISTS, parser)

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
        return quant_over_files.quantified_matcher(self.settings, quantifier,
                                                   matcher_on_existing_regular_file)

    @staticmethod
    def _expect_no_more_args_and_consume_current_line(parser: TokenParser):
        parser.report_superfluous_arguments_if_not_at_eol()
        parser.consume_current_line_as_string_of_remaining_part_of_current_line()
