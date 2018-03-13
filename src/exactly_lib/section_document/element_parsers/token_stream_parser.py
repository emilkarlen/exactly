import types
from contextlib import contextmanager
from typing import Callable, TypeVar, Iterable, Sequence, Tuple, Dict

from exactly_lib.help_texts.instruction_arguments import NEGATION_ARGUMENT_STR
from exactly_lib.section_document.element_parsers.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.misc_utils import new_token_stream
from exactly_lib.section_document.element_parsers.token_stream import TokenStream, LookAheadState
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.util import logic_types
from exactly_lib.util.cli_syntax.elements.argument import OptionName, Option
from exactly_lib.util.cli_syntax.option_parsing import matches
from exactly_lib.util.cli_syntax.option_syntax import option_syntax
from exactly_lib.util.messages import expected_found
from exactly_lib.util.parse.token import Token

T = TypeVar('T')

TokenParserType = TypeVar('TokenParserType')  # Substitute for TokenParser, since cannot be used inside class


class TokenParser:
    """
    Utility for implementing parsers backed by a :class:`TokenStream`.

    Encapsulates parsing/syntax of command-line-options and strings,
    and hides the representation of the source (the :class:`TokenStream`).
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
            self.error(error_message_format_string)

    def require_existing_valid_head_token(self, syntax_element_name: str):
        if self._token_stream.is_null:
            self.error('Missing ' + syntax_element_name)
        self.require_head_token_has_valid_syntax(syntax_element_name)

    @property
    def is_at_eol(self) -> bool:
        remaining_part_of_current_line = self.token_stream.remaining_part_of_current_line
        return not remaining_part_of_current_line or remaining_part_of_current_line.isspace()

    @property
    def has_current_line(self) -> bool:
        return not self.token_stream.is_at_end

    def require_is_at_eol(self, error_message_format_string: str):
        if not self.is_at_eol:
            self.error(error_message_format_string)

    def require_is_not_at_eol(self, error_message_format_string: str,
                              extra_format_map: dict = None):
        if self.is_at_eol:
            self.error(error_message_format_string, extra_format_map)

    def require_head_token_has_valid_syntax(self, error_message_format_string: str = ''):
        if self._lookahead_token_has_invalid_syntax():
            err_msg_separator = ': ' if error_message_format_string else ''
            self.error(
                error_message_format_string + err_msg_separator +
                'Invalid syntax: ' +
                self.token_stream.head_syntax_error_description)

    def report_superfluous_arguments_if_not_at_eol(self):
        remaining = self.token_stream.remaining_part_of_current_line.strip()
        if len(remaining) != 0:
            self.error('Superfluous arguments: `{}`'.format(remaining))

    @property
    def remaining_part_of_current_line(self) -> str:
        return self.token_stream.remaining_part_of_current_line

    def consume_current_line_as_plain_string(self) -> str:
        return self.token_stream.consume_remaining_part_of_current_line_as_plain_string()

    def consume_mandatory_token(self, error_message_format_string: str) -> Token:
        if self._token_stream.is_null:
            self.error(error_message_format_string)
        return self.token_stream.consume()

    def consume_mandatory_string_argument(self, error_message_format_string: str) -> str:
        token = self.consume_mandatory_token(error_message_format_string)
        return token.string

    def consume_optional_negation_operator(self) -> logic_types.ExpectationType:
        is_negated = self.consume_and_return_true_if_first_argument_is_unquoted_and_equals(NEGATION_ARGUMENT_STR)
        return logic_types.from_is_negated(is_negated)

    def consume_and_return_true_if_first_argument_is_unquoted_and_equals(self, expected: str) -> bool:
        if self.token_stream.is_null:
            return False
        head = self.token_stream.head
        if head.is_plain and head.string == expected:
            self.token_stream.consume()
            return True
        return False

    def consume_mandatory_constant_string_that_must_be_unquoted_and_equal(
            self,
            expected_constants: Iterable[str],
            constant_2_ret_val: Callable[[str], T],
            error_message_header_template: str = '') -> T:
        """
        Consumes the first token if it is an unquoted string that is equal to the expected string.

        :param expected_constants: collection of names=strings. Must support the Python 'in' operator

        :param constant_2_ret_val: Transforms the constant string to the return value.
        If None, the string constant is returned.

        :return: The constant that matched

        :raises :class:`SingleInstructionInvalidArgumentException' None of the constants were found,
        or there is no remaining arguments on the current line.
        """

        def constants_list() -> str:
            return ' or '.join(['"' + constant + '"' for constant in expected_constants])

        if self.token_stream.is_null:
            return self.error(error_message_header_template + ': Missing {__CONSTANTS__}',
                              {'__CONSTANTS__': constants_list()})

        head = self.token_stream.head
        if head.is_quoted:
            err_msg = 'Expecting unquoted {}.\nFound: `{}\''.format(
                constants_list(),
                head.source_string)
            raise SingleInstructionInvalidArgumentException(err_msg)

        plain_head = head.string
        if plain_head not in expected_constants:
            err_msg_tmpl = error_message_header_template + ': Expecting {__CONSTS__}.\nFound: `{__ACTUAL__}\''
            return self.error(err_msg_tmpl,
                              {'__CONSTS__': constants_list(),
                               '__ACTUAL__': plain_head
                               })
        self.token_stream.consume()

        return constant_2_ret_val(plain_head)

    def consume_mandatory_unquoted_string(self,
                                          syntax_element_name: str,
                                          must_be_on_current_line: bool,
                                          ) -> str:
        """
        Consumes the first token if it is an unquoted string.

        :type must_be_on_current_line: Tells if the string must be found on the current line.
        :return: The unquoted string

        :raises :class:`SingleInstructionInvalidArgumentException' The parser is at end of file,
        or if the must_be_on_current_line is True but the current line is empty.
        """

        if self.token_stream.is_null:
            return self.error('Missing argument for ' + syntax_element_name)
        if self._lookahead_token_has_invalid_syntax():
            return self.error('Invalid syntax of ' + syntax_element_name)
        if self.is_at_eol and must_be_on_current_line:
            return self.error('Missing argument for ' + syntax_element_name)

        head = self.token_stream.head
        if head.is_quoted:
            err_msg = 'Expecting unquoted {}.\nFound: `{}\''.format(
                syntax_element_name,
                head.source_string)
            raise SingleInstructionInvalidArgumentException(err_msg)

        self.token_stream.consume()
        return head.string

    def consume_mandatory_constant_unquoted_string(self,
                                                   expected_string: str,
                                                   must_be_on_current_line: bool,
                                                   ):
        """
        Consumes the first token if it is an unquoted string.

        :type must_be_on_current_line: Tells if the string must be found on the current line.
        :return: The unquoted string

        :raises :class:`SingleInstructionInvalidArgumentException' The parser is at end of file,
        or if the must_be_on_current_line is True but the current line is empty.
        """
        actual_string = self.consume_mandatory_unquoted_string(expected_string, must_be_on_current_line)
        if actual_string != expected_string:
            raise SingleInstructionInvalidArgumentException(expected_found.unexpected_lines(
                expected_string,
                actual_string))

    def consume_optional_constant_string_that_must_be_unquoted_and_equal(self,
                                                                         expected_constants: Sequence[str]) -> str:
        """
        Consumes the first token if it is an unquoted string that is equal to one of the expected string constants.
        :param expected_constants: collection of names=strings. Must support the Python 'in' operator
        :return: None iff no match, else the constant that matched
        """
        if self.token_stream.is_null or self.is_at_eol:
            return None
        head = self.token_stream.head
        if head.is_quoted:
            return None
        if head.string in expected_constants:
            self.token_stream.consume()
            return head.string
        return None

    def parse_mandatory_string_that_must_be_unquoted(self,
                                                     syntax_element_name: str,
                                                     string_handler: Callable[[str], T],
                                                     must_be_on_current_line: bool) -> T:
        """
        Consumes the first token if it is an unquoted string.
        :param must_be_on_current_line: If True, the string must appear on the current line.
        :param syntax_element_name: Syntax name of mandatory string
        :param string_handler: A function that is given the parsed unquoted string
        :return: Return value from string_handler
        """
        string = self.consume_mandatory_unquoted_string(syntax_element_name, must_be_on_current_line)
        return string_handler(string)

    def consume_and_handle_first_matching_option(self,
                                                 return_value_if_no_match: T,
                                                 key_handler: Callable[[str], T],
                                                 key_and_option_name_list: Sequence[Tuple[str, OptionName]],
                                                 ):
        """
        Looks at the current argument and checks if it is any of a given set of options,
        and returns a value that corresponds to that option.

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

    def consume_and_handle_optional_option(self,
                                           return_value_if_no_match,
                                           argument_parser: types.FunctionType,
                                           option_name: OptionName,
                                           ):
        """
        Looks at the current argument and checks if it is the given option,
        and, if it is, returns the value from the given parser.

        A default value is returned if the the current token is not the given option,
        or if there are no tokens.

        :param option_name: Option to match
        :param return_value_if_no_match: Value to return if next token does not match any of the given
         `OptionName`:s.
         :param argument_parser: Is given this parser object as argument, after the option token has been consumed.
         The return value from this function is returned if the option matches the head token
        """
        if self.token_stream.is_null:
            return return_value_if_no_match
        elif matches(option_name, self.token_stream.head.source_string):
            self.token_stream.consume()
            return argument_parser(self)
        else:
            return return_value_if_no_match

    def parse_choice_of_optional_option(self,
                                        continuation_if_present: types.FunctionType,
                                        continuation_if_not_present: types.FunctionType,
                                        option_name: OptionName,
                                        ):
        """
        Looks at the current argument and checks if it is the given option.
        Depending on if the option is present:
        - present: consume it and continue parsing using designated parser
        - not present: continue parsing using designated parser

        :param option_name: Option to match

        :param continuation_if_present: Is given this parser object as argument,
         after the option token has been consumed.
         The return value from this function is returned if the option matches the head token

        :param continuation_if_not_present: Is given this parser object as argument,
         with unmodified "input stream".
         The return value from this function is returned if the option does not match the head token
        """
        if self.token_stream.is_null:
            return continuation_if_not_present(self)
        elif matches(option_name, self.token_stream.head.source_string):
            self.token_stream.consume()
            return continuation_if_present(self)
        else:
            return continuation_if_not_present(self)

    def head_matches(self, option_name: OptionName) -> bool:
        if self.token_stream.is_null:
            return False
        return matches(option_name, self.token_stream.head.source_string)

    def parse_optional_command(self, command_name_2_parser: Dict[str, Callable[[TokenParserType], T]]) -> T:
        """
        Checks if the first token is one of a given set of commands.  If the token
        matches a command, then invokes the parser that belongs to the command.

        Each command is a plain string.

        If the token is quoted, then it does not match any command, even if the
        string inside the quotes is equal to one of the commands.

        :param command_name_2_parser: string -> method that takes this parse as argument. Must not return None

        :return: None if (parser is at end of line, or no choice matches). Else
        result from the parser for the command (which must not be None).
        """

        command = self.consume_optional_constant_string_that_must_be_unquoted_and_equal(command_name_2_parser)
        if command is None:
            return None
        return command_name_2_parser[command](self)

    def parse_mandatory_command(self,
                                command_name_2_parser: Dict[str, Callable[[TokenParserType], T]],
                                syntax_element_name: str) -> T:
        """
        A variant of parse_optional_command ,where the command is mandatory.

        :raises `SingleInstructionInvalidArgumentException': The command is not found
        """
        self.require_existing_valid_head_token(syntax_element_name)
        command_name = self.consume_mandatory_unquoted_string(syntax_element_name, False)
        if command_name not in command_name_2_parser:
            return self.error('Invalid ' + syntax_element_name)
        return command_name_2_parser[command_name](self)

    def parse_mandatory_option(self, option_name_2_parser: dict):
        """
        A variant of parse_optional_command ,where the command is mandatory.

        :raises `SingleInstructionInvalidArgumentException': The command is not found
        """

        def expecting_an_option() -> str:
            options = option_name_2_parser.keys()
            options_str = '|'.join(map(option_syntax, options))
            return 'Expecting : {}{}\nFound     : {}'.format(
                '' if len(options) <= 1 else 'one of ',
                options_str,
                self.remaining_part_of_current_line)

        if self.token_stream.is_null:
            raise SingleInstructionInvalidArgumentException(expecting_an_option())
        elif self._lookahead_token_has_invalid_syntax():
            self.require_head_token_has_valid_syntax(expecting_an_option())

        key_and_option_name_list = [
            (option_name, option_name)
            for option_name in option_name_2_parser.keys()
        ]

        def key_handler(x):
            return x

        actual_option = self.consume_and_handle_first_matching_option(None,
                                                                      key_handler,
                                                                      key_and_option_name_list)
        if actual_option is None:
            raise SingleInstructionInvalidArgumentException(expecting_an_option())
        else:
            return option_name_2_parser[actual_option](self)

    def consume_optional_option_with_mandatory_argument(self, option_with_arg: Option) -> Token:
        """

        :param option_with_arg: An option that has an argument
        :return: None if head does not match the option. Otherwise the option argument
        """
        if not self.head_matches(option_with_arg.name):
            return None
        actual_option_name = self.token_stream.consume()
        return self.consume_mandatory_token('Missing {arg} argument for {option}'.format(
            arg=option_with_arg.argument,
            option=actual_option_name.string))

    @property
    def token_stream(self) -> TokenStream:
        return self._token_stream

    def error(self,
              error_message_format_string: str,
              extra_format_map: dict = None):

        format_map = self.error_message_format_map
        if extra_format_map:
            format_map = dict(list(self.error_message_format_map.items()) + list(extra_format_map.items()))

        err_msg = error_message_format_string.format_map(format_map)

        raise SingleInstructionInvalidArgumentException(err_msg)

    def _lookahead_token_has_invalid_syntax(self) -> bool:
        return self.token_stream.look_ahead_state is LookAheadState.SYNTAX_ERROR


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


def token_parser_with_additional_error_message_format_map(parser: TokenParser,
                                                          additional_error_message_format_map: dict
                                                          ) -> TokenParser:
    combined_error_message_format_map = dict(list(parser.error_message_format_map.items()) +
                                             list(additional_error_message_format_map.items()))

    return TokenParser(parser.token_stream,
                       combined_error_message_format_map)


@contextmanager
def from_parse_source(source: ParseSource,
                      consume_last_line_if_is_at_eol_after_parse: bool = False,
                      consume_last_line_if_is_at_eof_after_parse: bool = False):
    """
    Gives a :class:`TokenParserPrime` backed by the given :class:`ParseSource`.

    The source of the :class:`TokenParserPrime` is the remaining sources of the :class:`ParseSource`
    """
    tp = new_token_parser(source.remaining_source)
    yield tp
    source.consume(tp.token_stream.position)
    if consume_last_line_if_is_at_eol_after_parse and source.is_at_eol:
        source.consume_current_line()
    elif consume_last_line_if_is_at_eof_after_parse and source.is_at_eof:
        source.consume_current_line()


@contextmanager
def from_remaining_part_of_current_line_of_parse_source(parse_source: ParseSource):
    """
    Gives a :class:`TokenParserPrime` backed by the given :class:`ParseSource`.

    The source of the :class:`TokenParserPrime` is the remaining part of the current line of the :class:`ParseSource`
    """
    tp = new_token_parser(parse_source.remaining_part_of_current_line)
    yield tp
    parse_source.consume(tp.token_stream.position)
