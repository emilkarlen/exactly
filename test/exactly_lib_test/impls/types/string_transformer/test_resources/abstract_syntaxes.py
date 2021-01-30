from typing import Sequence

from exactly_lib.impls.types.string_transformer import names
from exactly_lib_test.symbol.test_resources import token_sequences as symbol_tok_seq
from exactly_lib_test.test_resources.source import abstract_syntax_impls
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntax import ProgramAbsStx
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.abstract_syntax import \
    StringTransformerAbsStx


class CustomStringTransformerAbsStx(StringTransformerAbsStx):
    def __init__(self, tokens: TokenSequence):
        self._tokens = tokens

    @staticmethod
    def of_str(value: str) -> StringTransformerAbsStx:
        return CustomStringTransformerAbsStx(TokenSequence.singleton(value))

    def tokenization(self) -> TokenSequence:
        return self._tokens


def symbol_reference_followed_by_superfluous_string_on_same_line(
        symbol_name: str = 'STRING_TRANSFORMER_SYMBOL',
) -> StringTransformerAbsStx:
    return CustomStringTransformerAbsStx(
        TokenSequence.concat([
            symbol_tok_seq.SymbolReferenceAsEitherPlainNameOrReferenceSyntax(symbol_name),
            TokenSequence.singleton('superfluous')
        ])
    )


class RunProgramAbsStx(StringTransformerAbsStx):
    def __init__(self, program: ProgramAbsStx):
        self._program = program

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.singleton(names.RUN_PROGRAM_TRANSFORMER_NAME),
            TokenSequence.optional_new_line(),
            self._program.tokenization(),
        ])


class StringTransformerCompositionAbsStx(abstract_syntax_impls.DelegateAbsStx,
                                         StringTransformerAbsStx):
    def __init__(self,
                 transformers: Sequence[StringTransformerAbsStx],
                 within_parens: bool,
                 allow_elements_on_separate_lines: bool,
                 ):
        super().__init__(
            abstract_syntax_impls.InfixOperatorAbsStx(
                self.operator_name(),
                transformers,
                within_parens,
                allow_elements_on_separate_lines)
        )

    @staticmethod
    def operator_name() -> str:
        return names.SEQUENCE_OPERATOR_NAME
