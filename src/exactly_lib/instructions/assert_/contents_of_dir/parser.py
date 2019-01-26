from exactly_lib.instructions.assert_.contents_of_dir import impl_utils
from exactly_lib.instructions.assert_.contents_of_dir.impl_utils import FilesSource
from exactly_lib.instructions.assert_.utils import assertion_part
from exactly_lib.instructions.assert_.utils.assertion_part import AssertionPart, \
    IdentityAssertionPartWithValidationAndReferences
from exactly_lib.section_document.element_parsers import token_stream_parser
from exactly_lib.section_document.element_parsers.section_element_parsers import \
    InstructionParserWithoutSourceFileLocationInfo
from exactly_lib.section_document.element_parsers.token_stream_parser import \
    token_parser_with_additional_error_message_format_map
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.pre_or_post_validation import ConstantSuccessValidator
from exactly_lib.test_case_utils.files_matcher import config
from exactly_lib.test_case_utils.files_matcher import parse_files_matcher
from exactly_lib.test_case_utils.parse import parse_file_ref


class Parser(InstructionParserWithoutSourceFileLocationInfo):
    def __init__(self):
        self.format_map = {
            'PATH': config.PATH_ARGUMENT.name,
        }

    def parse_from_source(self,
                          source: ParseSource,
                          must_be_on_current_line: bool = True) -> AssertPhaseInstruction:
        with token_stream_parser.from_parse_source(
                source,
                consume_last_line_if_is_at_eof_after_parse=True) as token_parser:
            assert isinstance(token_parser,
                              token_stream_parser.TokenParser), 'Must have a TokenParser'  # Type info for IDE
            token_parser = token_parser_with_additional_error_message_format_map(token_parser,
                                                                                 self.format_map)
            if must_be_on_current_line:
                token_parser.require_is_not_at_eol('Missing {PATH} argument')

            path_to_check = parse_file_ref.parse_file_ref_from_token_parser(config.ACTUAL_RELATIVITY_CONFIGURATION,
                                                                            token_parser)

            actual_path_checker_assertion_part = self._actual_path_checker_assertion_part(path_to_check)

            files_matcher_resolver = parse_files_matcher.parse_files_matcher(token_parser,
                                                                             must_be_on_current_line=False)

            token_parser.report_superfluous_arguments_if_not_at_eol()
            token_parser.consume_current_line_as_string_of_remaining_part_of_current_line()

            assertions = assertion_part.compose(
                actual_path_checker_assertion_part,
                impl_utils.FilesMatcherAsDirContentsAssertionPart(files_matcher_resolver),
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
            impl_utils.AssertPathIsExistingDirectory(),
        )
