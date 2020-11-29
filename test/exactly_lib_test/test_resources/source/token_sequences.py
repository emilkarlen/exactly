from typing import Sequence

from exactly_lib.util import collection
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


class WithinParens(TokenSequence):
    def __init__(self, value: TokenSequence):
        self._value = value

    @property
    def tokens(self) -> Sequence[Token]:
        return (
                ['(', tokens.OPTIONAL_NEW_LINE] +
                list(self._value.tokens) +
                [tokens.OPTIONAL_NEW_LINE, ')']
        )


class InfixOperator(TokenSequence):
    def __init__(self,
                 operator: str,
                 operands: Sequence[TokenSequence],
                 allow_elements_on_separate_lines: bool,
                 ):
        self._operator = operator
        self._operands = operands
        self._allow_elements_on_separate_lines = allow_elements_on_separate_lines

    @property
    def tokens(self) -> Sequence[Token]:
        tok_sequences = collection.intersperse_list(self._operator_tok_seq(),
                                                    self._operands)
        return TokenSequence.concat(tok_sequences).tokens

    def _operator_tok_seq(self) -> TokenSequence:
        return (
            TokenSequence.sequence((tokens.OPTIONAL_NEW_LINE,
                                    self._operator,
                                    tokens.OPTIONAL_NEW_LINE))
            if self._allow_elements_on_separate_lines
            else
            TokenSequence.singleton(self._operator)
        )


def maybe_within_parens(value: TokenSequence, within_parens: bool) -> TokenSequence:
    return (
        WithinParens(value)
        if within_parens
        else
        value
    )
