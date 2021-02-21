from abc import ABC
from typing import Optional, Sequence

from exactly_lib.definitions import path as path_texts
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.tcfs.relative_path_options import REL_OPTIONS_MAP
from exactly_lib.util.parse.token import QuoteType
from exactly_lib_test.test_resources.source import token_sequences
from exactly_lib_test.test_resources.source import tokens
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.types.path.test_resources.abstract_syntax import PathAbsStx
from exactly_lib_test.type_val_deps.types.string.test_resources import abstract_syntaxes as str_abs_stx
from exactly_lib_test.type_val_deps.types.string.test_resources.abstract_syntax import NonHereDocStringAbsStx
from exactly_lib_test.type_val_deps.types.string.test_resources.abstract_syntaxes import StringLiteralAbsStx


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
            REL_OPTIONS_MAP[self._relativity_option]._option_name,
        )


class PathStringAbsStx(PathAbsStx):
    def __init__(self, string: StringLiteralAbsStx):
        self.string = string

    @staticmethod
    def of_plain_str(string: str) -> 'PathStringAbsStx':
        return PathStringAbsStx(StringLiteralAbsStx(string))

    @staticmethod
    def of_shlex_quoted(unquoted_path_str: str) -> 'PathStringAbsStx':
        return PathStringAbsStx(StringLiteralAbsStx.of_shlex_quoted(unquoted_path_str))

    @staticmethod
    def of_plain_components(components: Sequence[str]) -> 'PathStringAbsStx':
        return PathStringAbsStx.of_plain_str('/'.join(components))

    def tokenization(self) -> TokenSequence:
        return self.string.tokenization()


class PathWRelativityAbsStx(PathAbsStx, ABC):
    def __init__(self,
                 relativity: RelativityAbsStx,
                 name: NonHereDocStringAbsStx,
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


def file_name_from_components__str(components: Sequence[str]) -> str:
    return '/'.join(components)


def file_name_from_components(components: Sequence[str],
                              quoting: Optional[QuoteType] = None,
                              ) -> NonHereDocStringAbsStx:
    return StringLiteralAbsStx(file_name_from_components__str(components),
                               quoting)


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

    @staticmethod
    def of_rel_opt(
            relativity: RelOptionType,
            name: str,
            quoting_: Optional[QuoteType] = None,
    ) -> 'PathWConstNameAbsStx':
        return PathWConstNameAbsStx(OptionRelativityAbsStx(relativity), name, quoting_)

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
