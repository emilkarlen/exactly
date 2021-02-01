from abc import ABC
from typing import Sequence

from exactly_lib.definitions import logic
from exactly_lib.definitions.primitives import file_matcher
from exactly_lib_test.symbol.test_resources import token_sequences as symbol_tok_seq
from exactly_lib_test.test_resources.source import abstract_syntax_impls
from exactly_lib_test.test_resources.source import abstract_syntax_impls as abstract_syntaxes
from exactly_lib_test.test_resources.source import token_sequences
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.types.file_matcher.test_resources.abstract_syntax import FileMatcherAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntax import ProgramAbsStx


class CustomFileMatcherAbsStx(FileMatcherAbsStx):
    def __init__(self, tokens: TokenSequence):
        self._tokens = tokens

    @staticmethod
    def of_str(value: str) -> FileMatcherAbsStx:
        return CustomFileMatcherAbsStx(TokenSequence.singleton(value))

    def tokenization(self) -> TokenSequence:
        return self._tokens


def symbol_reference_followed_by_superfluous_string_on_same_line(
        symbol_name: str = 'FILE_MATCHER_SYMBOL_NAME',
) -> FileMatcherAbsStx:
    return CustomFileMatcherAbsStx(
        TokenSequence.concat([
            symbol_tok_seq.SymbolReferenceAsEitherPlainNameOrReferenceSyntax(symbol_name),
            TokenSequence.singleton('superfluous')
        ])
    )


class FileMatcherInfixOpAbsStx(abstract_syntax_impls.InfixOperatorAbsStx,
                               FileMatcherAbsStx):
    def __init__(self,
                 operator: str,
                 operands: Sequence[FileMatcherAbsStx],
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
            operands: Sequence[FileMatcherAbsStx],
            within_parens: bool = False,
            allow_elements_on_separate_lines: bool = False,

    ) -> 'FileMatcherInfixOpAbsStx':
        return FileMatcherInfixOpAbsStx(
            logic.OR_OPERATOR_NAME,
            operands,
            within_parens,
            allow_elements_on_separate_lines,
        )

    @staticmethod
    def conjunction(
            operands: Sequence[FileMatcherAbsStx],
            within_parens: bool = False,
            allow_elements_on_separate_lines: bool = False,

    ) -> 'FileMatcherInfixOpAbsStx':
        return FileMatcherInfixOpAbsStx(
            logic.AND_OPERATOR_NAME,
            operands,
            within_parens,
            allow_elements_on_separate_lines,
        )


class PathArgumentPositionAbsStx(AbstractSyntax, ABC):
    pass


class PathArgumentPositionDefault(PathArgumentPositionAbsStx):
    def tokenization(self) -> TokenSequence:
        return TokenSequence.empty()


class PathArgumentPositionLast(PathArgumentPositionAbsStx):
    def tokenization(self) -> TokenSequence:
        return token_sequences.Option.of_option_name(file_matcher.PROGRAM_ARG_OPTION__LAST.name)


class PathArgumentPositionMarker(PathArgumentPositionAbsStx):
    def __init__(self, marker: str):
        self.marker = marker

    def tokenization(self) -> TokenSequence:
        return token_sequences.OptionWMandatoryValue.of_option_name(
            file_matcher.PROGRAM_ARG_OPTION__MARKER.name,
            TokenSequence.singleton(self.marker)
        )


class RunProgramAbsStx(FileMatcherAbsStx):
    def __init__(self,
                 program: ProgramAbsStx,
                 path_argument_position: PathArgumentPositionAbsStx,
                 ):
        self._program = program
        self._path_argument_position = path_argument_position

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.singleton(file_matcher.PROGRAM_MATCHER_NAME),
            TokenSequence.optional_new_line(),
            abstract_syntaxes.OptionallyOnNewLine(self._path_argument_position).tokenization(),
            self._program.tokenization(),
        ])
