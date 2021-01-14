import enum
from abc import ABC
from typing import Optional, Sequence

from exactly_lib.impls.types.program import syntax_elements
from exactly_lib.util.parse.token import QuoteType
from exactly_lib_test.symbol.test_resources import token_sequences as symbol_tok_seq
from exactly_lib_test.tcfs.test_resources.abstract_syntax import PathAbsStx
from exactly_lib_test.test_resources.source import token_sequences
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.types.string.test_resources import abstract_syntax as string_abs_stx
from exactly_lib_test.type_val_deps.types.string.test_resources.abstract_syntax import NonHereDocStringAbsStx


class ArgumentAbsStx(AbstractSyntax, ABC):
    pass


class ArgumentOfSymbolReferenceAbsStx(ArgumentAbsStx):
    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name

    def tokenization(self) -> TokenSequence:
        return symbol_tok_seq.SymbolReferenceAsReferenceSyntax(self.symbol_name)


class ArgumentOfStringAbsStx(ArgumentAbsStx):
    def __init__(self, string: NonHereDocStringAbsStx):
        self.string = string

    @staticmethod
    def of_str(argument: str,
               quoting: Optional[QuoteType] = None,
               ) -> ArgumentAbsStx:
        return ArgumentOfStringAbsStx(string_abs_stx.StringLiteralAbsStx(argument, quoting))

    @staticmethod
    def of_shlex_quoted(argument: str) -> ArgumentAbsStx:
        return ArgumentOfStringAbsStx(
            string_abs_stx.StringLiteralAbsStx.of_shlex_quoted(argument)
        )

    def tokenization(self) -> TokenSequence:
        return self.string.tokenization()


class ArgumentOfTextUntilEndOfLineAbsStx(ArgumentAbsStx):
    def __init__(self, text_until_end_of_line: NonHereDocStringAbsStx):
        self.text_until_end_of_line = text_until_end_of_line

    @staticmethod
    def of_str(text_until_end_of_line: str) -> 'ArgumentOfTextUntilEndOfLineAbsStx':
        return ArgumentOfTextUntilEndOfLineAbsStx(
            string_abs_stx.StringLiteralAbsStx(text_until_end_of_line)
        )

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.singleton(syntax_elements.REMAINING_PART_OF_CURRENT_LINE_AS_LITERAL_MARKER),
            self.text_until_end_of_line.tokenization()
        ])


class NonSymLinkFileType(enum.Enum):
    REGULAR = 1
    DIRECTORY = 2


class ArgumentOfExistingPathAbsStx(ArgumentAbsStx):
    PATH_OPTIONS = {
        None: syntax_elements.EXISTING_PATH_OPTION_NAME,
        NonSymLinkFileType.REGULAR: syntax_elements.EXISTING_FILE_OPTION_NAME,
        NonSymLinkFileType.DIRECTORY: syntax_elements.EXISTING_DIR_OPTION_NAME,
    }

    def __init__(self,
                 path: PathAbsStx,
                 file_type: Optional[NonSymLinkFileType] = None
                 ):
        self.path = path
        self.file_type = file_type

    def tokenization(self) -> TokenSequence:
        return token_sequences.OptionWMandatoryValue.of_option_name(
            self.PATH_OPTIONS[self.file_type],
            self.path.tokenization(),
        )


class ArgumentsAbsStx(AbstractSyntax):
    def __init__(self, arguments: Sequence[ArgumentAbsStx]):
        self._arguments = arguments

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            argument.tokenization()
            for argument in self._arguments
        ]
        )
