from typing import Sequence, Optional

from exactly_lib.util.parse.token import QuoteType
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.types.list_.test_resources.abstract_syntax import ListAbsStx, ListElementAbsStx
from exactly_lib_test.type_val_deps.types.string.test_resources import abstract_syntaxes as str_abs_stx
from exactly_lib_test.type_val_deps.types.string.test_resources.abstract_syntax import NonHereDocStringAbsStx


class ListElementStringAbsStx(ListElementAbsStx):
    def __init__(self, string: NonHereDocStringAbsStx):
        self.string = string

    @staticmethod
    def of_str(value: str,
               quoting: Optional[QuoteType] = None,
               ) -> 'ListElementStringAbsStx':
        return ListElementStringAbsStx(
            str_abs_stx.StringLiteralAbsStx(value, quoting)
        )

    def tokenization(self) -> TokenSequence:
        return self.string.tokenization()


class EmptyListAbsStx(ListAbsStx):
    def tokenization(self) -> TokenSequence:
        return TokenSequence.empty()


class NonEmptyListAbsStx(ListAbsStx):
    def __init__(self, elements: Sequence[ListElementAbsStx]):
        if not elements:
            raise NotImplementedError('Non Empty List: sequence of elements is empty')
        self.elements = elements

    @staticmethod
    def singleton(element: ListElementAbsStx) -> 'NonEmptyListAbsStx':
        return NonEmptyListAbsStx((element,))

    @staticmethod
    def singleton_string(element: NonHereDocStringAbsStx) -> 'NonEmptyListAbsStx':
        return NonEmptyListAbsStx.singleton(ListElementStringAbsStx(element))

    @staticmethod
    def singleton_string__str(element: str,
                              quoting: Optional[QuoteType] = None,
                              ) -> 'NonEmptyListAbsStx':
        return NonEmptyListAbsStx.singleton_string(
            str_abs_stx.StringLiteralAbsStx(element, quoting)
        )

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            element.tokenization()
            for element in self.elements
        ])
