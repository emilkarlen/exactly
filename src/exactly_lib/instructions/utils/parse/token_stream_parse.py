import types

from exactly_lib.instructions.assert_.utils.negation_of_assertion import NEGATION_ARGUMENT_STR
from exactly_lib.instructions.utils.expectation_type import ExpectationType
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token_stream import TokenStream
from exactly_lib.symbol.path_resolver import FileRefResolver
from exactly_lib.test_case_utils.parse import parse_file_ref
from exactly_lib.test_case_utils.parse.misc_utils import new_token_stream
from exactly_lib.test_case_utils.parse.rel_opts_configuration import RelOptionArgumentConfiguration
from exactly_lib.util.cli_syntax.option_parsing import matches


class TokenParser:
    """
    Utility for implementing parsers backed by a :class:`TokenStream`.
    
    Encapsulates parsing/syntax of command-line-options and strings.
    """

    def __init__(self,
                 token_stream: TokenStream,
                 error_message_format_map: dict = None):
        """
        
        :param token_stream: Token stream to read tokens from.
        :param error_message_format_map: Map to pass to string.format_map as the map argument.
        """
        self._token_stream = token_stream
        self.error_message_format_map = {} if error_message_format_map is None else error_message_format_map

    def if_null_then_invalid_arguments(self, error_message_format_string: str):
        if self._token_stream.is_null:
            self._error(error_message_format_string)

    @property
    def is_at_eol(self) -> bool:
        return self.token_stream.remaining_part_of_current_line.isspace()

    def require_is_at_eol(self, error_message_format_string: str):
        if not self.is_at_eol:
            self._error(error_message_format_string)

    def report_superfluous_arguments_if_not_at_eol(self):
        remaining = self.token_stream.remaining_part_of_current_line.strip()
        if len(remaining) != 0:
            self._error('Superfluous arguments: `{}`'.format(remaining))

    def consume_mandatory_string_argument(self, error_message_format_string: str) -> str:
        if self._token_stream.is_null:
            self._error(error_message_format_string)
        ret_val = self.token_stream.head.string
        self.token_stream.consume()
        return ret_val

    def consume_optional_negation_operator(self) -> ExpectationType:
        is_negated = self.consume_and_return_true_if_first_argument_is_unquoted_and_equals(NEGATION_ARGUMENT_STR)
        return ExpectationType.NEGATIVE if is_negated else ExpectationType.POSITIVE

    def consume_and_return_true_if_first_argument_is_unquoted_and_equals(self, expected: str) -> bool:
        if self.token_stream.is_null:
            return False
        head = self.token_stream.head
        if head.is_plain and head.string == expected:
            self.token_stream.consume()
            return True
        return False

    def consume_mandatory_constant_string_that_must_be_unquoted_and_equal(self, expected: str):
        if self.token_stream.is_null:
            raise SingleInstructionInvalidArgumentException('Expecting "{}"'.format(expected))
        head = self.token_stream.head
        if head.is_quoted:
            err_msg = 'Expecting unquoted "{}".\nFound: `{}\''.format(
                expected,
                head.source_string)
            raise SingleInstructionInvalidArgumentException(err_msg)
        plain_head = head.string
        if plain_head != expected:
            err_msg = 'Expecting "{}".\nFound: `{}\''.format(
                expected,
                head.source_string)
            raise SingleInstructionInvalidArgumentException(err_msg)
        self.token_stream.consume()

    def consume_and_handle_first_matching_option(self,
                                                 return_value_if_no_match,
                                                 key_handler: types.FunctionType,
                                                 key_and_option_name_list: list,
                                                 ):
        """
        Looks at the current argument and checks if it is any of a given set of options,
        and and returns a value that corresponds to that option.

        A default value is returned if the the current argument is not any of the given options,
        or if there are no arguments.

        :param key_and_option_name_list: [(key, `OptionName`)]
        :param return_value_if_no_match: Value to return if next token does not match any of the given 
         `OptionName`:s.
         :param key_handler: Gives the return value from a key corresponding to
         the `OptionType` that matches the next token.
        """
        if self.token_stream.is_null:
            return return_value_if_no_match
        for key, option_name in key_and_option_name_list:
            if matches(option_name, self.token_stream.head.source_string):
                self.token_stream.consume()
                return key_handler(key)
        return return_value_if_no_match

    @property
    def token_stream(self) -> TokenStream:
        return self._token_stream

    def _error(self, error_message_format_string: str):
        err_msg = error_message_format_string.format_map(self.error_message_format_map)
        raise SingleInstructionInvalidArgumentException(err_msg)

    def consume_file_ref(self, conf: RelOptionArgumentConfiguration) -> FileRefResolver:
        return parse_file_ref.parse_file_ref(self._token_stream, conf)


def new_token_parser(source: str,
                     error_message_format_map: dict = None) -> TokenParser:
    """
    Constructs a :class:`TokenParser`
    :argument error_message_format_map: strings that are replaced in error messages
    via :func:`str#format`
    :type error_message_format_map: dict str -> str
    :rtype: :class:`TokenParser`
    :raises :class:`SingleInstructionInvalidArgumentException` Source has invalid syntax
    """
    return TokenParser(new_token_stream(source),
                       error_message_format_map)
