from exactly_lib.help_texts import instruction_arguments
from exactly_lib.instructions.assert_.contents_of_dir.assertions import common, emptiness, num_files, quant_over_files
from exactly_lib.instructions.assert_.contents_of_dir.config import PATH_ARGUMENT, ACTUAL_RELATIVITY_CONFIGURATION
from exactly_lib.instructions.assert_.utils.expression import parse as expression_parse
from exactly_lib.instructions.assert_.utils.file_contents import parse_file_contents_assertion_part
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations import token_stream_parse_prime
from exactly_lib.section_document.parser_implementations.section_element_parsers import InstructionParser
from exactly_lib.section_document.parser_implementations.token_stream_parse_prime import TokenParserPrime
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher
from exactly_lib.test_case_utils.parse import parse_file_ref
from exactly_lib.util.logic_types import Quantifier
from exactly_lib.util.messages import grammar_options_syntax
from . import config


class Parser(InstructionParser):
    def __init__(self):
        self.format_map = {
            'PATH': PATH_ARGUMENT.name,
        }

    def parse(self, source: ParseSource) -> AssertPhaseInstruction:
        with token_stream_parse_prime.from_parse_source(
                source,
                consume_last_line_if_is_at_eof_after_parse=True) as token_parser:
            assert isinstance(token_parser,
                              token_stream_parse_prime.TokenParserPrime), 'Must have a TokenParser'  # Type info for IDE

            path_to_check = parse_file_ref.parse_file_ref_from_token_parser(ACTUAL_RELATIVITY_CONFIGURATION,
                                                                            token_parser)
            file_selection = parse_file_matcher.parse_optional_selection_resolver(token_parser)
            expectation_type = token_parser.consume_optional_negation_operator()
            instructions_parser = _CheckInstructionParser(common.Settings(expectation_type,
                                                                          path_to_check,
                                                                          file_selection))

            instruction = instructions_parser.parse(token_parser)
            token_parser.report_superfluous_arguments_if_not_at_eol()
            token_parser.consume_current_line_as_plain_string()
            return instruction


class _CheckInstructionParser:
    def __init__(self, settings: common.Settings):
        self.settings = settings
        self.command_parsers = {
            config.NUM_FILES_CHECK_ARGUMENT: self.parse_num_files_check,
            config.EMPTINESS_CHECK_ARGUMENT: self.parse_empty_check,
            instruction_arguments.ALL_QUANTIFIER_ARGUMENT: self.parse_file_quantified_assertion__all,
            instruction_arguments.EXISTS_QUANTIFIER_ARGUMENT: self.parse_file_quantified_assertion__exists,
        }
        self.missing_check_description = 'Missing argument for check :' + grammar_options_syntax.alternatives_list(
            self.command_parsers)

    def parse(self, parser: TokenParserPrime) -> AssertPhaseInstruction:
        return parser.parse_mandatory_command(self.command_parsers,
                                              self.missing_check_description)

    def parse_empty_check(self, parser: TokenParserPrime) -> AssertPhaseInstruction:
        return emptiness.InstructionForEmptiness(self.settings)

    def parse_num_files_check(self, parser: TokenParserPrime) -> AssertPhaseInstruction:
        cmp_op_and_rhs = expression_parse.parse_integer_comparison_operator_and_rhs(
            parser,
            expression_parse.validator_for_non_negative)

        return num_files.InstructionForNumFiles(self.settings, cmp_op_and_rhs)

    def parse_file_quantified_assertion__all(self, parser: TokenParserPrime) -> AssertPhaseInstruction:
        return self._file_quantified_assertion(Quantifier.ALL, parser)

    def parse_file_quantified_assertion__exists(self, parser: TokenParserPrime) -> AssertPhaseInstruction:
        return self._file_quantified_assertion(Quantifier.EXISTS, parser)

    def _file_quantified_assertion(self,
                                   quantifier: Quantifier,
                                   parser: TokenParserPrime) -> AssertPhaseInstruction:
        parser.consume_mandatory_constant_unquoted_string(config.QUANTIFICATION_OVER_FILE_ARGUMENT,
                                                          must_be_on_current_line=True)
        actual_file_assertion_part = parse_file_contents_assertion_part.parse(parser)
        return quant_over_files.InstructionForQuantifiedAssertion(self.settings, quantifier, actual_file_assertion_part)
