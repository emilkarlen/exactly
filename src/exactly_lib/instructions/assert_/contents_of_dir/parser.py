from exactly_lib.definitions import instruction_arguments
from exactly_lib.instructions.assert_.contents_of_dir import files_matcher
from exactly_lib.instructions.assert_.contents_of_dir.assertions import common, emptiness, num_files, quant_over_files
from exactly_lib.instructions.assert_.contents_of_dir.assertions.common import DirContentsAssertionPart, \
    FilesMatcherAsDirContentsAssertionPart
from exactly_lib.instructions.assert_.contents_of_dir.config import PATH_ARGUMENT, ACTUAL_RELATIVITY_CONFIGURATION
from exactly_lib.instructions.assert_.contents_of_dir.files_matcher import FilesSource
from exactly_lib.instructions.assert_.utils import assertion_part
from exactly_lib.instructions.assert_.utils.assertion_part import AssertionPart, \
    IdentityAssertionPartWithValidationAndReferences
from exactly_lib.instructions.assert_.utils.file_contents.parts.contents_checkers import \
    IsExistingRegularFileAssertionPart, ComparisonActualFile
from exactly_lib.section_document.element_parsers import token_stream_parser
from exactly_lib.section_document.element_parsers.section_element_parsers import \
    InstructionParserWithoutSourceFileLocationInfo
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.pre_or_post_validation import ConstantSuccessValidator
from exactly_lib.test_case_utils.condition.integer import parse_integer_condition as expression_parse
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher
from exactly_lib.test_case_utils.parse import parse_file_ref
from exactly_lib.type_system.logic.string_matcher import FileToCheck
from exactly_lib.util.logic_types import Quantifier
from exactly_lib.util.messages import grammar_options_syntax
from . import config


class Parser(InstructionParserWithoutSourceFileLocationInfo):
    def __init__(self):
        self.format_map = {
            'PATH': PATH_ARGUMENT.name,
        }

    def parse_from_source(self, source: ParseSource) -> AssertPhaseInstruction:
        with token_stream_parser.from_parse_source(
                source,
                consume_last_line_if_is_at_eof_after_parse=True) as token_parser:
            assert isinstance(token_parser,
                              token_stream_parser.TokenParser), 'Must have a TokenParser'  # Type info for IDE

            path_to_check = parse_file_ref.parse_file_ref_from_token_parser(ACTUAL_RELATIVITY_CONFIGURATION,
                                                                            token_parser)

            actual_path_checker_assertion_part = self._actual_path_checker_assertion_part(path_to_check)

            files_matcher = parse_files_matcher(token_parser)

            assertions = assertion_part.compose(
                actual_path_checker_assertion_part,
                files_matcher,
            )

            return assertion_part.AssertionInstructionFromAssertionPart(assertions,
                                                                        None,
                                                                        lambda x: FilesSource(path_to_check))

    @staticmethod
    def _actual_path_checker_assertion_part(path_to_check: FileRefResolver
                                            ) -> AssertionPart[FilesSource, FilesSource]:
        return assertion_part.compose(
            IdentityAssertionPartWithValidationAndReferences(
                ConstantSuccessValidator(),
                path_to_check.references,
            ),
            common.AssertPathIsExistingDirectory(),
        )


def parse_files_matcher(parser: TokenParser) -> AssertionPart[FilesSource, FilesSource]:
    file_selection = parse_file_matcher.parse_optional_selection_resolver(parser)
    expectation_type = parser.consume_optional_negation_operator()

    files_matcher_parser = _FilesMatcherParserForSettings(
        files_matcher.Settings(expectation_type,
                               file_selection))
    return files_matcher_parser.parse(parser)


class _FilesMatcherParserForSettings:
    def __init__(self, settings: files_matcher.Settings):
        self.settings = settings
        self.command_parsers = {
            config.NUM_FILES_CHECK_ARGUMENT: self.parse_num_files_check,
            config.EMPTINESS_CHECK_ARGUMENT: self.parse_empty_check,
            instruction_arguments.ALL_QUANTIFIER_ARGUMENT: self.parse_file_quantified_assertion__all,
            instruction_arguments.EXISTS_QUANTIFIER_ARGUMENT: self.parse_file_quantified_assertion__exists,
        }
        self.missing_check_description = 'Missing argument for check :' + grammar_options_syntax.alternatives_list(
            self.command_parsers)

    def parse(self, parser: TokenParser) -> AssertionPart[FilesSource, FilesSource]:
        return parser.parse_mandatory_command(self.command_parsers,
                                              self.missing_check_description)

    def parse_empty_check(self, parser: TokenParser) -> AssertionPart[FilesSource, FilesSource]:
        self._expect_no_more_args_and_consume_current_line(parser)
        matcher_resolver = emptiness.EmptinessAssertion(self.settings)
        return FilesMatcherAsDirContentsAssertionPart(matcher_resolver)

    def parse_num_files_check(self, parser: TokenParser) -> DirContentsAssertionPart:
        cmp_op_and_rhs = expression_parse.parse_integer_comparison_operator_and_rhs(
            parser,
            expression_parse.validator_for_non_negative)

        self._expect_no_more_args_and_consume_current_line(parser)

        return num_files.NumFilesAssertion(self.settings, cmp_op_and_rhs)

    def parse_file_quantified_assertion__all(self, parser: TokenParser) -> DirContentsAssertionPart:
        return self._file_quantified_assertion(Quantifier.ALL, parser)

    def parse_file_quantified_assertion__exists(self, parser: TokenParser) -> DirContentsAssertionPart:
        return self._file_quantified_assertion(Quantifier.EXISTS, parser)

    def _file_quantified_assertion(self,
                                   quantifier: Quantifier,
                                   parser: TokenParser) -> DirContentsAssertionPart:
        from exactly_lib.instructions.assert_.utils.file_contents import parse_file_contents_assertion_part

        parser.consume_mandatory_constant_unquoted_string(config.QUANTIFICATION_OVER_FILE_ARGUMENT,
                                                          must_be_on_current_line=True)
        parser.consume_mandatory_constant_unquoted_string(
            instruction_arguments.QUANTIFICATION_SEPARATOR_ARGUMENT,
            must_be_on_current_line=True)
        assertion_on_existing_regular_file = parse_file_contents_assertion_part.parse(parser)

        return self._file_quantified_assertion_part(quantifier, assertion_on_existing_regular_file)

    def _file_quantified_assertion_part(self,
                                        quantifier: Quantifier,
                                        on_existing_regular_file: AssertionPart[ComparisonActualFile, FileToCheck]
                                        ) -> DirContentsAssertionPart:
        assertion_on_file = assertion_part.compose(IsExistingRegularFileAssertionPart(),
                                                   on_existing_regular_file)
        return quant_over_files.QuantifiedAssertion(self.settings, quantifier, assertion_on_file)

    @staticmethod
    def _expect_no_more_args_and_consume_current_line(parser: TokenParser):
        parser.report_superfluous_arguments_if_not_at_eol()
        parser.consume_current_line_as_string_of_remaining_part_of_current_line()
