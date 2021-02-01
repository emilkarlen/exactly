from typing import Sequence

from exactly_lib.definitions import logic
from exactly_lib_test.symbol.test_resources import token_sequences as symbol_tok_seq
from exactly_lib_test.test_resources.source import abstract_syntax_impls
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.types.integer_matcher.test_resources.abstract_syntax import IntegerMatcherAbsStx


class CustomIntegerMatcherAbsStx(IntegerMatcherAbsStx):
    def __init__(self, tokens: TokenSequence):
        self._tokens = tokens

    @staticmethod
    def of_str(value: str) -> IntegerMatcherAbsStx:
        return CustomIntegerMatcherAbsStx(TokenSequence.singleton(value))

    def tokenization(self) -> TokenSequence:
        return self._tokens


def symbol_reference_followed_by_superfluous_string_on_same_line(
        symbol_name: str = 'INTEGER_MATCHER_SYMBOL_NAME',
) -> IntegerMatcherAbsStx:
    return CustomIntegerMatcherAbsStx(
        TokenSequence.concat([
            symbol_tok_seq.SymbolReferenceAsEitherPlainNameOrReferenceSyntax(symbol_name),
            TokenSequence.singleton('superfluous')
        ])
    )


class IntegerMatcherInfixOpAbsStx(abstract_syntax_impls.InfixOperatorAbsStx,
                                  IntegerMatcherAbsStx):
    def __init__(self,
                 operator: str,
                 operands: Sequence[IntegerMatcherAbsStx],
                 within_parens: bool,
                 allow_elements_on_separate_lines: bool,
                 ):
        super().__init__(
            operator,
            operands,
            within_parens,
            allow_elements_on_separate_lines,
        )

    @staticmethod
    def disjunction(
            operands: Sequence[IntegerMatcherAbsStx],
            within_parens: bool = False,
            allow_elements_on_separate_lines: bool = False,

    ) -> 'IntegerMatcherInfixOpAbsStx':
        return IntegerMatcherInfixOpAbsStx(
            logic.OR_OPERATOR_NAME,
            operands,
            within_parens,
            allow_elements_on_separate_lines,
        )

    @staticmethod
    def conjunction(
            operands: Sequence[IntegerMatcherAbsStx],
            within_parens: bool = False,
            allow_elements_on_separate_lines: bool = False,

    ) -> 'IntegerMatcherInfixOpAbsStx':
        return IntegerMatcherInfixOpAbsStx(
            logic.AND_OPERATOR_NAME,
            operands,
            within_parens,
            allow_elements_on_separate_lines,
        )
