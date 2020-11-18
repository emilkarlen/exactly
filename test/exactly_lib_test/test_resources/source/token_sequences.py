from typing import Sequence

from exactly_lib.util.cli_syntax.elements.argument import OptionName
from exactly_lib_test.test_resources.source import tokens
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence, Token


class Option(TokenSequence):
    def __init__(self, option_name: str):
        self.option_name = option_name
        if not isinstance(option_name, str):
            raise NotImplementedError('Not a str: ' + str(option_name))

    @staticmethod
    def of_option_name(option: OptionName) -> 'Option':
        return Option(option.long)

    @property
    def tokens(self) -> Sequence[Token]:
        return [tokens.option(self.option_name)]


class OptionWMandatoryValue(TokenSequence):
    def __init__(self,
                 option_name: str,
                 value: TokenSequence,
                 ):
        self.option_name = option_name
        self.value = value
        if not isinstance(option_name, str):
            raise NotImplementedError('Not a str: ' + str(option_name))

    @staticmethod
    def of_option_name(option: OptionName,
                       value: TokenSequence,
                       ) -> 'OptionWMandatoryValue':
        return OptionWMandatoryValue(option.long, value)

    @property
    def tokens(self) -> Sequence[Token]:
        return (
                [tokens.option(self.option_name)] +
                [tokens.OPTIONAL_NEW_LINE] +
                list(self.value.tokens)
        )
