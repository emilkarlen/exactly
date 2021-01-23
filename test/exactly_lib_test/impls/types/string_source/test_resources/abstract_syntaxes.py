from abc import ABC
from typing import Sequence

from exactly_lib.definitions.primitives import string_transformer
from exactly_lib.impls.types.string_source import defs
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.parse.token import QuoteType
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib_test.impls.types.string_source.test_resources.abstract_syntax import StringSourceAbsStx
from exactly_lib_test.test_resources.source import token_sequences
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.types.path.test_resources.abstract_syntax import PathAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntax import ProgramAbsStx
from exactly_lib_test.type_val_deps.types.string.test_resources import abstract_syntaxes as str_abs_stx
from exactly_lib_test.type_val_deps.types.string.test_resources.abstract_syntax import StringAbsStx
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.abstract_syntax import \
    StringTransformerAbsStx


class TransformableStringSourceAbsStx(StringSourceAbsStx, ABC):
    pass


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


class StringSourceOfStringAbsStx(StringSourceAbsStx):
    def __init__(self, string: StringAbsStx):
        self.string = string

    @staticmethod
    def of_str(s: str, quoting: QuoteType) -> StringSourceAbsStx:
        return StringSourceOfStringAbsStx(
            str_abs_stx.StringLiteralAbsStx(s, quoting)
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
