from typing import Sequence

from exactly_lib.definitions import logic
from exactly_lib_test.impls.types.matcher.test_resources import abstract_syntaxes as matcher_abs_stx
from exactly_lib_test.symbol.test_resources import token_sequences as symbol_tok_seq
from exactly_lib_test.test_resources.source import abstract_syntax_impls
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.types.line_matcher.test_resources.abstract_syntax import LineMatcherAbsStx


class CustomLineMatcherAbsStx(LineMatcherAbsStx):
    def __init__(self, tokens: TokenSequence):
        self._tokens = tokens

    @staticmethod
    def of_str(value: str) -> LineMatcherAbsStx:
        return CustomLineMatcherAbsStx(TokenSequence.singleton(value))

    def tokenization(self) -> TokenSequence:
        return self._tokens


def symbol_reference_followed_by_superfluous_string_on_same_line(
        symbol_name: str = 'LINE_MATCHER_SYMBOL_NAME',
) -> LineMatcherAbsStx:
    return CustomLineMatcherAbsStx(
        TokenSequence.concat([
            symbol_tok_seq.SymbolReferenceAsEitherPlainNameOrReferenceSyntax(symbol_name),
            TokenSequence.singleton('superfluous')
        ])
    )


class LineMatcherConstantAbsStx(matcher_abs_stx.ConstantMatcherAbsStx,
                                LineMatcherAbsStx):
    pass


class LineMatcherInfixOpAbsStx(abstract_syntax_impls.InfixOperatorAbsStx,
                               LineMatcherAbsStx):
    def __init__(self,
                 operator: str,
                 operands: Sequence[LineMatcherAbsStx],
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
            operands: Sequence[LineMatcherAbsStx],
            within_parens: bool = False,
            allow_elements_on_separate_lines: bool = False,

    ) -> 'LineMatcherInfixOpAbsStx':
        return LineMatcherInfixOpAbsStx(
            logic.OR_OPERATOR_NAME,
            operands,
            within_parens,
            allow_elements_on_separate_lines,
        )

    @staticmethod
    def conjunction(
            operands: Sequence[LineMatcherAbsStx],
            within_parens: bool = False,
            allow_elements_on_separate_lines: bool = False,

    ) -> 'LineMatcherInfixOpAbsStx':
        return LineMatcherInfixOpAbsStx(
            logic.AND_OPERATOR_NAME,
            operands,
            within_parens,
            allow_elements_on_separate_lines,
        )
