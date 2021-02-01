from typing import Sequence

from exactly_lib.definitions import logic
from exactly_lib.definitions.primitives import matcher
from exactly_lib.impls.types.string_matcher import matcher_options
from exactly_lib_test.symbol.test_resources import token_sequences as symbol_tok_seq
from exactly_lib_test.test_resources.source import abstract_syntax_impls
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntax import ProgramAbsStx
from exactly_lib_test.type_val_deps.types.string_matcher.test_resources.abstract_syntax import StringMatcherAbsStx
from exactly_lib_test.type_val_deps.types.string_source.test_resources.abstract_syntax import StringSourceAbsStx


class CustomStringMatcherAbsStx(StringMatcherAbsStx):
    def __init__(self, tokens: TokenSequence):
        self._tokens = tokens

    @staticmethod
    def of_str(value: str) -> StringMatcherAbsStx:
        return CustomStringMatcherAbsStx(TokenSequence.singleton(value))

    def tokenization(self) -> TokenSequence:
        return self._tokens


def symbol_reference_followed_by_superfluous_string_on_same_line(
        symbol_name: str = 'STRING_MATCHER_SYMBOL_NAME',
) -> StringMatcherAbsStx:
    return CustomStringMatcherAbsStx(
        TokenSequence.concat([
            symbol_tok_seq.SymbolReferenceAsEitherPlainNameOrReferenceSyntax(symbol_name),
            TokenSequence.singleton('superfluous')
        ])
    )


class StringMatcherInfixOpAbsStx(abstract_syntax_impls.InfixOperatorAbsStx,
                                 StringMatcherAbsStx):
    def __init__(self,
                 operator: str,
                 operands: Sequence[StringMatcherAbsStx],
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
            operands: Sequence[StringMatcherAbsStx],
            within_parens: bool = False,
            allow_elements_on_separate_lines: bool = False,

    ) -> 'StringMatcherInfixOpAbsStx':
        return StringMatcherInfixOpAbsStx(
            logic.OR_OPERATOR_NAME,
            operands,
            within_parens,
            allow_elements_on_separate_lines,
        )

    @staticmethod
    def conjunction(
            operands: Sequence[StringMatcherAbsStx],
            within_parens: bool = False,
            allow_elements_on_separate_lines: bool = False,

    ) -> 'StringMatcherInfixOpAbsStx':
        return StringMatcherInfixOpAbsStx(
            logic.AND_OPERATOR_NAME,
            operands,
            within_parens,
            allow_elements_on_separate_lines,
        )


class RunProgramAbsStx(StringMatcherAbsStx):
    def __init__(self, program: ProgramAbsStx):
        self._program = program

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.singleton(matcher.RUN_PROGRAM),
            TokenSequence.optional_new_line(),
            self._program.tokenization(),
        ])


class EqualsAbsStx(StringMatcherAbsStx):
    def __init__(self, expected: StringSourceAbsStx):
        self._expected = expected

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.singleton(matcher_options.EQUALS_ARGUMENT),
            TokenSequence.optional_new_line(),
            self._expected.tokenization(),
        ])
