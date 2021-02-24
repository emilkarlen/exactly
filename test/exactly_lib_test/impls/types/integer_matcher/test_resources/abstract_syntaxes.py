from typing import Sequence, Optional

from exactly_lib.definitions import logic
from exactly_lib.impls.types.condition.comparators import ComparisonOperator
from exactly_lib.util.parse.token import QuoteType
from exactly_lib_test.impls.types.matcher.test_resources.abstract_syntaxes import NegationMatcherAbsStx
from exactly_lib_test.symbol.test_resources import token_sequences as symbol_tok_seq
from exactly_lib_test.test_resources.source import abstract_syntax_impls
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.types.integer_matcher.test_resources.abstract_syntax import IntegerMatcherAbsStx
from exactly_lib_test.type_val_deps.types.string_.test_resources.abstract_syntax import StringAbsStx
from exactly_lib_test.type_val_deps.types.string_.test_resources.abstract_syntaxes import StringLiteralAbsStx


class CustomIntegerMatcherAbsStx(IntegerMatcherAbsStx):
    def __init__(self, tokens: TokenSequence):
        self._tokens = tokens

    @staticmethod
    def empty() -> IntegerMatcherAbsStx:
        return CustomIntegerMatcherAbsStx(TokenSequence.empty())

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


class IntegerMatcherNegationAbsStx(NegationMatcherAbsStx,
                                   IntegerMatcherAbsStx):
    def __init__(self, operand: IntegerMatcherAbsStx):
        super().__init__(operand)


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


class IntegerMatcherComparisonAbsStx(IntegerMatcherAbsStx):
    def __init__(self,
                 operator: str,
                 operand: StringAbsStx,
                 ):
        self.operator = operator
        self.operand = operand

    @staticmethod
    def of_cmp_op(operator: ComparisonOperator,
                  operand: StringAbsStx,
                  ) -> 'IntegerMatcherComparisonAbsStx':
        return IntegerMatcherComparisonAbsStx(
            operator.name,
            operand,
        )

    @staticmethod
    def of_cmp_op__str(operator: ComparisonOperator,
                       operand: str,
                       quoting: Optional[QuoteType] = None,
                       ) -> 'IntegerMatcherComparisonAbsStx':
        return IntegerMatcherComparisonAbsStx.of_cmp_op(
            operator,
            StringLiteralAbsStx(operand, quoting),
        )

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.singleton(self.operator),
            self.operand.tokenization(),
        ])
