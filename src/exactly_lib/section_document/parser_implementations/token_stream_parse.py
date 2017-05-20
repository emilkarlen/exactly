from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token_stream2 import TokenStream2
from exactly_lib.util.cli_syntax.option_parsing import matches


class TokenParser:
    """
    Utility for implementing parsers backed by a `TokenStream2`.
    
    Encapsulates parsing/syntax of command-line-options and strings.
    """

    def __init__(self,
                 token_stream: TokenStream2,
                 error_message_format_map: dict):
        """
        
        :param token_stream: Token stream to read tokens from.
        :param error_message_format_map: Map to pass to string.format_map as the map argument.
        """
        self._token_stream = token_stream
        self.error_message_format_map = error_message_format_map

    def if_null_then_invalid_arguments(self, error_message_format_string: str):
        if self._token_stream.is_null:
            self._error(error_message_format_string)

    def require_is_at_eol(self, error_message_format_string: str):
        remaining = self.token_stream.remaining_part_of_current_line.strip()
        if len(remaining) != 0:
            self._error(error_message_format_string)

    def consume_mandatory_string_argument(self, error_message_format_string: str) -> str:
        if self._token_stream.is_null:
            self._error(error_message_format_string)
        ret_val = self.token_stream.head.string
        self.token_stream.consume()
        return ret_val

    def consume_and_handle_first_matching_option(self, key_and_option_name_list) -> list:
        """
        
        :param key_and_option_name_list: [(key, `OptionName`)] 
        :return: singleton list of [key] if an OptionName matches the head of the token stream. Otherwise []
        """
        if self.token_stream.is_null:
            return []
        for key, option_name in key_and_option_name_list:
            if matches(option_name, self.token_stream.head.source_string):
                self.token_stream.consume()
                return [key]
        return []

    @property
    def token_stream(self) -> TokenStream2:
        return self._token_stream

    def _error(self, error_message_format_string: str):
        err_msg = error_message_format_string.format_map(self.error_message_format_map)
        raise SingleInstructionInvalidArgumentException(err_msg)
