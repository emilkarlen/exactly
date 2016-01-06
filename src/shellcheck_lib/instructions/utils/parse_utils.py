import shlex

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
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
        self.t_and_tail_source = [] if source is None else source.split(maxsplit=1)

    @property
    def source(self) -> str:
        return self._source

    @property
    def is_null(self) -> bool:
        return not self.t_and_tail_source

    @property
    def head(self) -> str:
        return self.t_and_tail_source[0]

    @property
    def tail(self):  # -> TokenStream
        return TokenStream(self.tail_source)

    @property
    def tail_source_or_empty_string(self) -> str:
        ts = self.tail_source
        return '' if ts is None else ts

    @property
    def tail_source(self) -> str:
        if len(self.t_and_tail_source) == 1:
            return None
        else:
            return self.t_and_tail_source[1]
