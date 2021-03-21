from typing import Sequence, Optional, Callable

from exactly_lib.definitions import logic
from exactly_lib.definitions.test_case import reserved_words
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib_test.test_resources.source import token_sequences, layout
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence


class OptionalAbsStx(AbstractSyntax):
    def __init__(self,
                 optional: Optional[AbstractSyntax],
                 tokenizer: Callable[[TokenSequence], TokenSequence],
                 ):
        self._optional = optional
        self._tokenizer = tokenizer

    def tokenization(self) -> TokenSequence:
        return (
            TokenSequence.empty()
            if self._optional is None
            else
            self._tokenizer(self._optional.tokenization())
        )


class OptionalOptionWMandatoryArgumentAbsStx(AbstractSyntax):
    """An option w argument, if argument is present. Otherwise empty."""

    def __init__(self,
                 option_name: str,
                 argument: Optional[AbstractSyntax],
                 ):
        self._option_name = option_name
        self._argument = argument

    @staticmethod
    def of_option_name(option: a.OptionName,
                       argument: Optional[AbstractSyntax],
                       ) -> AbstractSyntax:
        return OptionalOptionWMandatoryArgumentAbsStx(
            option.long,
            argument,
        )

    def tokenization(self) -> TokenSequence:
        return (
            TokenSequence.empty()
            if self._argument is None
            else
            token_sequences.OptionWMandatoryValue(
                self._option_name,
                self._argument.tokenization()
            )
        )


class OptionallyOnNewLine(AbstractSyntax):
    def __init__(self, syntax: AbstractSyntax):
        self._syntax = syntax

    def tokenization(self) -> TokenSequence:
        element_tokens = self._syntax.tokenization()
        return (
            TokenSequence.empty()
            if not element_tokens
            else
            TokenSequence.concat([
                TokenSequence.optional_new_line(),
                element_tokens,
            ])
        )


class DelegateAbsStx(AbstractSyntax):
    def __init__(self, delegate: AbstractSyntax):
        self._delegate = delegate

    def tokenization(self) -> TokenSequence:
        return self._delegate.tokenization()


class WithinParensAbsStx(AbstractSyntax):
    def __init__(self,
                 element: AbstractSyntax,
                 end_paren_on_separate_line: bool = False,
                 ):
        self._element = element
        self._end_paren_on_separate_lines = end_paren_on_separate_line

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.singleton(reserved_words.PAREN_BEGIN),
            TokenSequence.optional_new_line(),
            self._element.tokenization(),
            self._end_paren()
        ])

    def _end_paren(self) -> TokenSequence:
        return (
            TokenSequence.sequence([layout.NEW_LINE, reserved_words.PAREN_END])
            if self._end_paren_on_separate_lines
            else
            TokenSequence.sequence([layout.OPTIONAL_NEW_LINE, reserved_words.PAREN_END])
        )


class CustomAbsStx(AbstractSyntax):
    def __init__(self, tokens: TokenSequence):
        self._tokens = tokens

    @staticmethod
    def empty() -> AbstractSyntax:
        return CustomAbsStx(TokenSequence.empty())

    @staticmethod
    def singleton(token: str) -> AbstractSyntax:
        return CustomAbsStx(TokenSequence.singleton(token))

    @staticmethod
    def of_str(s: str) -> AbstractSyntax:
        return CustomAbsStx(TokenSequence.singleton(s))

    def tokenization(self) -> TokenSequence:
        return self._tokens


class InfixOperatorAbsStx(AbstractSyntax):
    def __init__(self,
                 operator: str,
                 operands: Sequence[AbstractSyntax],
                 within_parens: bool,
                 allow_elements_on_separate_lines: bool,
                 ):
        if len(operands) < 2:
            raise ValueError('Infix operator: number of operands < 2: ' + str(len(operands)))
        self.operator = operator
        self.operands = operands
        self._within_parens = within_parens
        self._allow_elements_on_separate_lines = allow_elements_on_separate_lines

    def tokenization(self) -> TokenSequence:
        operands = [operand.tokenization() for operand in self.operands]
        return token_sequences.maybe_within_parens(
            token_sequences.InfixOperator(self.operator,
                                          operands,
                                          self._allow_elements_on_separate_lines),
            self._within_parens
        )


class NegationAbsStx(AbstractSyntax):
    def __init__(self, matcher: AbstractSyntax):
        self._matcher = matcher

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.singleton(logic.NOT_OPERATOR_NAME),
            TokenSequence.optional_new_line(),
            self._matcher.tokenization(),
        ])
