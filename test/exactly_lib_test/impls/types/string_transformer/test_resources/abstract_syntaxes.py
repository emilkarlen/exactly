from typing import Sequence, Optional

from exactly_lib.impls.types.string_transformer import names
from exactly_lib_test.symbol.test_resources import token_sequences as symbol_tok_seq
from exactly_lib_test.test_resources.source import abstract_syntax_impls, token_sequences
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.types.line_matcher.test_resources.abstract_syntax import LineMatcherAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntax import ProgramAbsStx
from exactly_lib_test.type_val_deps.types.string_.test_resources.abstract_syntax import StringAbsStx
from exactly_lib_test.type_val_deps.types.string_.test_resources.abstract_syntaxes import StringLiteralAbsStx
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
        symbol_name: str = 'STRING_TRANSFORMER_SYMBOL_NAME',
) -> StringTransformerAbsStx:
    return CustomStringTransformerAbsStx(
        TokenSequence.concat([
            symbol_tok_seq.SymbolReferenceAsEitherPlainNameOrReferenceSyntax(symbol_name),
            TokenSequence.singleton('superfluous')
        ])
    )


class ReplaceRegexAbsStx(StringTransformerAbsStx):
    def __init__(self,
                 regex_token: StringAbsStx,
                 replacement_token: StringAbsStx,
                 preserve_new_lines: bool,
                 lines_filter: Optional[LineMatcherAbsStx],
                 ):
        self.lines_filter = abstract_syntax_impls.OptionalOptionWMandatoryArgumentAbsStx.of_option_name(
            names.LINES_SELECTION_OPTION_NAME,
            lines_filter,
        )
        self.preserve_new_lines = preserve_new_lines
        self.regex_token = regex_token
        self.replacement_token = replacement_token

    @staticmethod
    def of_str(regex_token: str,
               replacement_token: str,
               preserve_new_lines: bool,
               lines_filter: Optional[LineMatcherAbsStx],
               ) -> 'ReplaceRegexAbsStx':
        return ReplaceRegexAbsStx(
            StringLiteralAbsStx(regex_token),
            StringLiteralAbsStx(replacement_token),
            preserve_new_lines,
            lines_filter,
        )

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.singleton(names.REPLACE_TRANSFORMER_NAME),
            TokenSequence.optional_new_line(),
            token_sequences.FollowedByOptionalNewLineIfNonEmpty(
                self.lines_filter.tokenization()
            ),
            token_sequences.FollowedByOptionalNewLineIfNonEmpty(
                token_sequences.OptionalOption.of_option_name(
                    names.PRESERVE_NEW_LINES_OPTION_NAME,
                    self.preserve_new_lines,
                )
            ),
            self.regex_token.tokenization(),
            TokenSequence.optional_new_line(),
            self.replacement_token.tokenization(),
        ])


class RunProgramAbsStx(StringTransformerAbsStx):
    def __init__(self, program: ProgramAbsStx):
        self._program = program

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.singleton(names.RUN_PROGRAM_TRANSFORMER_NAME),
            TokenSequence.optional_new_line(),
            self._program.tokenization(),
        ])


class StringTransformerCompositionAbsStx(abstract_syntax_impls.InfixOperatorAbsStx,
                                         StringTransformerAbsStx):
    def __init__(self,
                 transformers: Sequence[StringTransformerAbsStx],
                 within_parens: bool,
                 allow_elements_on_separate_lines: bool,
                 ):
        super().__init__(
            self.operator_name(),
            transformers,
            within_parens,
            allow_elements_on_separate_lines,
        )

    @staticmethod
    def operator_name() -> str:
        return names.SEQUENCE_OPERATOR_NAME
