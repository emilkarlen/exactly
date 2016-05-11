import io
import shlex

from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException


def split_arguments_list_string(arguments: str) -> list:
    """
    :raises SingleInstructionInvalidArgumentException: The arguments string cannot be parsed.
    """
    try:
        return shlex.split(arguments)
    except ValueError:
        raise SingleInstructionInvalidArgumentException('Invalid quoting of arguments')


def is_option_argument(argument: str) -> bool:
    return argument[0] == '-'


def ensure_is_not_option_argument(argument: str):
    """
    :raises SingleInstructionInvalidArgumentException: The arguments is an option argument.
    """
    if is_option_argument(argument):
        raise SingleInstructionInvalidArgumentException('An option argument was not expected here: {}'.format(argument))


class TokenStream:
    def __init__(self, source: str):
        self._source = source
        if source is None:
            self._head = None
            self._tail_source_or_empty_string = ''
        else:
            source_io = io.StringIO(source)
            lexer = shlex.shlex(source_io, posix=True)
            lexer.whitespace_split = True
            self._head = lexer.get_token()
            self._tail_source_or_empty_string = source[source_io.tell():].lstrip()

    @property
    def source(self) -> str:
        return self._source

    @property
    def is_null(self) -> bool:
        return self._head is None

    @property
    def head(self) -> str:
        return self._head

    @property
    def tail(self):  # -> TokenStream
        return TokenStream(self.tail_source)

    @property
    def tail_source_or_empty_string(self) -> str:
        return self._tail_source_or_empty_string

    @property
    def tail_source(self) -> str:
        if self._tail_source_or_empty_string:
            return self._tail_source_or_empty_string
        else:
            return None
