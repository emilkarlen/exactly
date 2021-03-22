from typing import Sequence, Optional

from exactly_lib.definitions.primitives import string_transformer
from exactly_lib.impls.types.string_source import defs
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.parse.token import QuoteType
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib_test.test_resources.source import token_sequences, abstract_syntax_impls
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.types.path.test_resources.abstract_syntax import PathAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntax import ProgramAbsStx
from exactly_lib_test.type_val_deps.types.string_.test_resources import abstract_syntaxes as str_abs_stx
from exactly_lib_test.type_val_deps.types.string_.test_resources import rich_abstract_syntaxes as rich_str_abs_stx
from exactly_lib_test.type_val_deps.types.string_.test_resources.abstract_syntax import StringAbsStx
from exactly_lib_test.type_val_deps.types.string_.test_resources.rich_abstract_syntax import RichStringAbsStx
from exactly_lib_test.type_val_deps.types.string_source.test_resources.abstract_syntax import StringSourceAbsStx, \
    TransformableStringSourceAbsStx
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.abstract_syntax import \
    StringTransformerAbsStx


class TransformedStringSourceAbsStx(StringSourceAbsStx):
    def __init__(self,
                 transformed: TransformableStringSourceAbsStx,
                 transformer: StringTransformerAbsStx,
                 ):
        self.transformed = transformed
        self.transformer = transformer

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            self.transformed.tokenization(),
            TokenSequence.optional_new_line(),
            token_sequences.OptionWMandatoryValue.of_option_name(
                string_transformer.WITH_TRANSFORMED_CONTENTS_OPTION_NAME,
                self.transformer.tokenization(),
            ),
        ])


class CustomStringSourceAbsStx(StringSourceAbsStx):
    def __init__(self, tokens: TokenSequence):
        self._tokens = tokens

    @staticmethod
    def missing_value() -> StringSourceAbsStx:
        return CustomStringSourceAbsStx(TokenSequence.empty())

    @staticmethod
    def w_superfluous() -> StringSourceAbsStx:
        return CustomStringSourceAbsStx(
            TokenSequence.concat([
                StringSourceOfStringAbsStx.of_str('valid').tokenization(),
                TokenSequence.sequence('superfluous'),
            ])
        )

    def tokenization(self) -> TokenSequence:
        return self._tokens


class StringSourceOfStringAbsStx(TransformableStringSourceAbsStx):
    def __init__(self, string: RichStringAbsStx):
        self.string = string

    @staticmethod
    def of_str(s: str, quoting: Optional[QuoteType] = None) -> 'StringSourceOfStringAbsStx':
        return StringSourceOfStringAbsStx.of_plain(
            str_abs_stx.StringLiteralAbsStx(s, quoting)
        )

    @staticmethod
    def of_str_hard(s: str) -> 'StringSourceOfStringAbsStx':
        return StringSourceOfStringAbsStx.of_str(s, QuoteType.HARD)

    @staticmethod
    def of_plain(string: StringAbsStx) -> 'StringSourceOfStringAbsStx':
        return StringSourceOfStringAbsStx(
            rich_str_abs_stx.PlainStringAbsStx(string)
        )

    def tokenization(self) -> TokenSequence:
        return self.string.tokenization()


class StringSourceOfFileAbsStx(TransformableStringSourceAbsStx):
    def __init__(self, file: PathAbsStx):
        self.file = file

    def tokenization(self) -> TokenSequence:
        return token_sequences.OptionWMandatoryValue.of_option_name(
            defs.FILE_OPTION,
            self.file.tokenization(),
        )


class StringSourceOfProgramAbsStx(StringSourceAbsStx):
    def __init__(self,
                 output_file: ProcOutputFile,
                 program: ProgramAbsStx,
                 ignore_exit_code: bool = False,
                 ):
        self.output_file = output_file
        self.program = program
        self.ignore_exit_code = ignore_exit_code

    def tokenization(self) -> TokenSequence:
        program_w_optional_ignore_exit_code = (
            token_sequences.OptionWMandatoryValue.of_option_name(
                defs.IGNORE_EXIT_CODE,
                self.program.tokenization(),
            )
            if self.ignore_exit_code
            else
            self.program.tokenization()
        )
        return token_sequences.OptionWMandatoryValue.of_option_name(
            defs.PROGRAM_OUTPUT_OPTIONS[self.output_file],
            program_w_optional_ignore_exit_code,
        )


class StringSourceWithinParensAbsStx(StringSourceAbsStx):
    """NOTE This class allows arbitrary levels of parens, which is not valid syntax.
    Only single level of parens is allowed.
    """

    def __init__(self,
                 string_source: StringSourceAbsStx,
                 end_paren_on_separate_line: bool = False,
                 ):
        self._syntax = abstract_syntax_impls.WithinParensAbsStx(string_source,
                                                                end_paren_on_separate_line)

    def tokenization(self) -> TokenSequence:
        return self._syntax.tokenization()


class TransformableAbsStxBuilder:
    def __init__(self, untransformed: TransformableStringSourceAbsStx):
        self._untransformed = untransformed

    def without_transformation(self) -> TransformableStringSourceAbsStx:
        return self._untransformed

    def with_transformation(self, transformer: StringTransformerAbsStx) -> StringSourceAbsStx:
        return TransformedStringSourceAbsStx(self._untransformed, transformer)

    def with_and_without_transformer_cases(self, transformer: StringTransformerAbsStx,
                                           ) -> Sequence[NameAndValue[StringSourceAbsStx]]:
        return [
            NameAndValue('without transformation', self.without_transformation()),
            NameAndValue('with transformation', self.with_transformation(transformer)),
        ]
