from abc import ABC
from typing import Optional, Sequence

from exactly_lib.definitions import path as path_texts
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.tcfs.relative_path_options import REL_OPTIONS_MAP
from exactly_lib.util.parse.token import QuoteType
from exactly_lib_test.symbol.test_resources import token_sequences as symbol_tok_seq
from exactly_lib_test.test_resources.source import token_sequences
from exactly_lib_test.test_resources.source import tokens
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.types.string.test_resources import abstract_syntax as str_abs_stx
from exactly_lib_test.type_val_deps.types.string.test_resources.abstract_syntax import StringAbsStx, StringLiteralAbsStx


class RelativityAbsStx(AbstractSyntax, ABC):
    pass


class DefaultRelativityAbsStx(RelativityAbsStx):
    def tokenization(self) -> TokenSequence:
        return TokenSequence.empty()


class SymbolRelativityAbsStx(RelativityAbsStx):
    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name

    def tokenization(self) -> TokenSequence:
        return TokenSequence.sequence([
            tokens.option(path_texts.REL_SYMBOL_OPTION_NAME.long),
            self.symbol_name,
        ])


class OptionRelativityAbsStx(RelativityAbsStx):
    def __init__(self, relativity_option: RelOptionType):
        self._relativity_option = relativity_option

    @property
    def relativity_option(self) -> RelOptionType:
        return self._relativity_option

    def tokenization(self) -> TokenSequence:
        return token_sequences.Option.of_option_name(
            REL_OPTIONS_MAP[self._relativity_option].option_name,
        )


class PathAbsStx(AbstractSyntax, ABC):
    pass


class PathStringAbsStx(PathAbsStx):
    def __init__(self, string: StringLiteralAbsStx):
        self.string = string

    @staticmethod
    def of_plain_str(string: str) -> 'PathStringAbsStx':
        return PathStringAbsStx(StringLiteralAbsStx(string))

    @staticmethod
    def of_plain_components(components: Sequence[str]) -> 'PathStringAbsStx':
        return PathStringAbsStx.of_plain_str('/'.join(components))

    def tokenization(self) -> TokenSequence:
        return self.string.tokenization()


class PathSymbolReferenceAbsStx(PathAbsStx):
    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name

    def tokenization(self) -> TokenSequence:
        return symbol_tok_seq.SymbolReferenceAsReferenceSyntax(self.symbol_name)


class PathWRelativityAbsStx(PathAbsStx, ABC):
    def __init__(self,
                 relativity: RelativityAbsStx,
                 name: StringAbsStx,
                 ):
        self._relativity = relativity
        self._name_abs_stx = name

    def tokenization(self) -> TokenSequence:
        # TODO 2020-11-18
        # Add optional-new-line between relativity and name
        # (if relativity is non-empty)?
        # Not sure if this is supported.
        return TokenSequence.concat([
            self._relativity.tokenization(),
            self._name_abs_stx.tokenization(),
        ])


class PathWConstNameAbsStx(PathWRelativityAbsStx, ABC):
    def __init__(self,
                 relativity: RelativityAbsStx,
                 name: str,
                 quoting_: Optional[QuoteType] = None,
                 ):
        super().__init__(relativity,
                         str_abs_stx.StringLiteralAbsStx(name, quoting_),
                         )
        self._name = name

    @property
    def name(self) -> str:
        return self._name


class RelSymbolPathAbsStx(PathWConstNameAbsStx):
    def __init__(self,
                 symbol_name: str,
                 name: str,
                 quoting_: Optional[QuoteType] = None,
                 ):
        super().__init__(SymbolRelativityAbsStx(symbol_name),
                         name, quoting_,
                         )


class RelOptPathAbsStx(PathWConstNameAbsStx):
    def __init__(self,
                 relativity_option: RelOptionType,
                 name: str,
                 quoting_: Optional[QuoteType] = None,
                 ):
        super().__init__(OptionRelativityAbsStx(relativity_option),
                         name, quoting_,
                         )
        self._relativity_option = relativity_option

    @property
    def relativity_option(self) -> RelOptionType:
        return self._relativity_option


class DefaultRelPathAbsStx(PathWConstNameAbsStx):
    def __init__(self,
                 name: str,
                 quoting_: Optional[QuoteType] = None,
                 ):
        super().__init__(DefaultRelativityAbsStx(),
                         name, quoting_,
                         )
