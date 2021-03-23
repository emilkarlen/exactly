import enum
from typing import Optional, Sequence

from exactly_lib.impls.types.program import syntax_elements
from exactly_lib.type_val_deps.types.list_ import defs
from exactly_lib.util.parse.token import QuoteType
from exactly_lib_test.symbol.test_resources import token_sequences as symbol_tok_seq
from exactly_lib_test.test_resources.source import token_sequences
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.types.path.test_resources.abstract_syntax import PathAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.argument_abs_stx import ArgumentAbsStx
from exactly_lib_test.type_val_deps.types.string_.test_resources import abstract_syntaxes as str_abs_stx
from exactly_lib_test.type_val_deps.types.string_.test_resources import rich_abstract_syntaxes as _rs_abs_stx
from exactly_lib_test.type_val_deps.types.string_.test_resources.rich_abstract_syntax import RichStringAbsStx


class ArgumentOfSymbolReferenceAbsStx(ArgumentAbsStx):
    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name

    def tokenization(self) -> TokenSequence:
        return symbol_tok_seq.SymbolReferenceAsReferenceSyntax(self.symbol_name)


class ContinuationTokenFollowedByArgumentAbsStx(ArgumentAbsStx):
    CONTINUATION_TOKEN = defs.CONTINUATION_TOKEN

    def __init__(self, argument_on_next_line: ArgumentAbsStx):
        self._argument_on_next_line = argument_on_next_line

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.singleton(defs.CONTINUATION_TOKEN),
            TokenSequence.new_line(),
            self._argument_on_next_line.tokenization(),
        ])


class ArgumentOfRichStringAbsStx(ArgumentAbsStx):
    def __init__(self, value: RichStringAbsStx):
        self.value = value

    @staticmethod
    def of_str(argument: str,
               quoting: Optional[QuoteType] = None,
               ) -> 'ArgumentOfRichStringAbsStx':
        return ArgumentOfRichStringAbsStx(
            _rs_abs_stx.PlainStringAbsStx(
                str_abs_stx.StringLiteralAbsStx(argument, quoting)
            )
        )

    @staticmethod
    def of_str_until_eol(text_until_end_of_line: str) -> 'ArgumentOfRichStringAbsStx':
        return ArgumentOfRichStringAbsStx(
            _rs_abs_stx.TextUntilEndOfLineAbsStx(text_until_end_of_line)
        )

    def tokenization(self) -> TokenSequence:
        return self.value.tokenization()


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
