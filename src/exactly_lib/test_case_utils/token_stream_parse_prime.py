import types
from contextlib import contextmanager

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.misc_utils import new_token_stream
from exactly_lib.section_document.parser_implementations.token_stream import TokenStream
from exactly_lib.test_case_utils.negation_of_predicate import NEGATION_ARGUMENT_STR
from exactly_lib.util import expectation_type
from exactly_lib.util.cli_syntax.elements.argument import OptionName, Option
from exactly_lib.util.cli_syntax.option_parsing import matches
from exactly_lib.util.parse.token import Token


class TokenParserPrime:
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

    @property
    def is_at_eol(self) -> bool:
        return self.token_stream.remaining_part_of_current_line.isspace()

    def require_is_at_eol(self, error_message_format_string: str):
        if not self.is_at_eol:
            self.error(error_message_format_string)

    def require_is_not_at_eol(self, error_message_format_string: str):
        if self.is_at_eol:
            self.error(error_message_format_string)

    def report_superfluous_arguments_if_not_at_eol(self):
        remaining = self.token_stream.remaining_part_of_current_line.strip()
        if len(remaining) != 0:
            self.error('Superfluous arguments: `{}`'.format(remaining))

    def consume_mandatory_token(self, error_message_format_string: str) -> Token:
        if self._token_stream.is_null:
            self.error(error_message_format_string)
        return self.token_stream.consume()

    def consume_mandatory_string_argument(self, error_message_format_string: str) -> str:
        token = self.consume_mandatory_token(error_message_format_string)
        return token.string

    def consume_optional_negation_operator(self) -> expectation_type.ExpectationType:
        is_negated = self.consume_and_return_true_if_first_argument_is_unquoted_and_equals(NEGATION_ARGUMENT_STR)
        return expectation_type.from_is_negated(is_negated)

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
            expected_constants,
            constant_2_ret_val: types.FunctionType = None,
            error_message_header_template: str = ''):
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
                              __CONSTANTS__=constants_list())

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
                              __CONSTS__=constants_list(),
                              __ACTUAL__=plain_head)
        self.token_stream.consume()

        if constant_2_ret_val is not None:
            return constant_2_ret_val(plain_head)

        return plain_head

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

    def consume_optional_constant_string_that_must_be_unquoted_and_equal(self, expected_constants) -> str:
        """
        Consumes the first token if it is an unquoted string that is equal to the expected string.
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
                                                     string_handler: types.FunctionType,
                                                     must_be_on_current_line: bool):
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

    def consume_and_handle_optional_option(self,
                                           return_value_if_no_match,
                                           argument_parser: types.FunctionType,
                                           option_name: OptionName,
                                           ):
        """
        Looks at the current argument and checks if it is the given option,
        and, if it is, returns the value from the given parser.

        A default value is returned if the the current argument is not the given option,
        or if there are no arguments.

        :param key_and_option_name_list: [(key, `OptionName`)]
        :param return_value_if_no_match: Value to return if next token does not match any of the given
         `OptionName`:s.
         :param key_handler: Gives the return value from a key corresponding to
         the `OptionType` that matches the next token.
        """
        if self.token_stream.is_null:
            return return_value_if_no_match
        elif matches(option_name, self.token_stream.head.source_string):
            self.token_stream.consume()
            return argument_parser(self)
        else:
            return return_value_if_no_match

    def head_matches(self, option_name: OptionName) -> bool:
        if self.token_stream.is_null:
            return False
        return matches(option_name, self.token_stream.head.source_string)

    def parse_optional_command(self, command_name_2_parser: dict):
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
                                command_name_2_parser: dict,
                                error_message_format_string: str):
        """
        A variant of parse_optional_command ,where the command is mandatory.

        :raises `SingleInstructionInvalidArgumentException': The command is not found
        """
        command = self.parse_optional_command(command_name_2_parser)
        if command is None:
            raise SingleInstructionInvalidArgumentException(self.error(error_message_format_string))
        return command

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

    def error(self, error_message_format_string: str, **kwargs):

        format_map = self.error_message_format_map
        if kwargs:
            format_map = dict(list(self.error_message_format_map.items()) + list(kwargs.items()))

        err_msg = error_message_format_string.format_map(format_map)

        raise SingleInstructionInvalidArgumentException(err_msg)


def new_token_parser(source: str,
                     error_message_format_map: dict = None) -> TokenParserPrime:
    """
    Constructs a :class:`TokenParser`
    :argument error_message_format_map: strings that are replaced in error messages
    via :func:`str#format`
    :type error_message_format_map: dict str -> str
    :rtype: :class:`TokenParser`
    :raises :class:`SingleInstructionInvalidArgumentException` Source has invalid syntax
    """
    return TokenParserPrime(new_token_stream(source),
                            error_message_format_map)


def token_parser_with_additional_error_message_format_map(parser: TokenParserPrime,
                                                          additional_error_message_format_map: dict
                                                          ) -> TokenParserPrime:
    combined_error_message_format_map = dict(list(parser.error_message_format_map.items()) +
                                             list(additional_error_message_format_map.items()))

    return TokenParserPrime(parser.token_stream,
                            combined_error_message_format_map)


@contextmanager
def from_parse_source(parse_source: ParseSource):
    """
    Gives a :class:`TokenParserPrime` backed by the given :class:`ParseSource`.

    The source of the :class:`TokenParserPrime` is the remaining sources of the :class:`ParseSource`
    """
    tp = new_token_parser(parse_source.remaining_source)
    yield tp
    parse_source.consume(tp.token_stream.position)


@contextmanager
def from_remaining_part_of_current_line_of_parse_source(parse_source: ParseSource):
    """
    Gives a :class:`TokenParserPrime` backed by the given :class:`ParseSource`.

    The source of the :class:`TokenParserPrime` is the remaining part of the current line of the :class:`ParseSource`
    """
    tp = new_token_parser(parse_source.remaining_part_of_current_line)
    yield tp
    parse_source.consume(tp.token_stream.position)
