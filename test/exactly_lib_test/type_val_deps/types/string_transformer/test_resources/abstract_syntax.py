from abc import ABC
from typing import Sequence

from exactly_lib.impls.types.string_transformer import names
from exactly_lib_test.symbol.test_resources import token_sequences as symbol_tok_seq
from exactly_lib_test.test_resources.source import abstract_syntax_impls
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence


class StringTransformerAbsStx(AbstractSyntax, ABC):
    pass


class StringTransformerSymbolReferenceAbsStx(StringTransformerAbsStx):
    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name

    def tokenization(self) -> TokenSequence:
        return symbol_tok_seq.SymbolReferenceAsEitherPlainNameOrReferenceSyntax(self.symbol_name)


class StringTransformerCompositionAbsStx(abstract_syntax_impls.DelegateAbsStx,
                                         StringTransformerAbsStx):
    def __init__(self,
                 transformers: Sequence[StringTransformerAbsStx],
                 within_parens: bool,
                 allow_elements_on_separate_lines: bool,
                 ):
        super().__init__(
            abstract_syntax_impls.InfixOperatorAbsStx(
                names.SEQUENCE_OPERATOR_NAME,
                transformers,
                within_parens,
                allow_elements_on_separate_lines)
        )
