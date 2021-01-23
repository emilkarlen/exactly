from typing import Sequence

from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.parse.token import QUOTE_CHAR_FOR_TYPE, QuoteType
from exactly_lib_test.impls.types.string_source.test_resources.abstract_syntaxes import StringSourceOfStringAbsStx
from exactly_lib_test.impls.types.string_transformers.test_resources.abstract_syntaxes import \
    CustomStringTransformerAbsStx
from exactly_lib_test.symbol.test_resources.symbol_syntax import NOT_A_VALID_SYMBOL_NAME, A_VALID_SYMBOL_NAME, \
    NOT_A_VALID_SYMBOL_NAME_NOR_PRIMITIVE_GRAMMAR_ELEMENT_NAME
from exactly_lib_test.type_val_deps.types.program.test_resources.argument_abs_stx import ArgumentAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.argument_abs_stxs import ArgumentOfStringAbsStx
from exactly_lib_test.type_val_deps.types.string.test_resources import abstract_syntaxes as str_abs_stx
from exactly_lib_test.type_val_deps.types.string_source.test_resources.abstract_syntax import StringSourceAbsStx
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.abstract_syntax import \
    StringTransformerAbsStx
from exactly_lib_test.util.test_resources.quoting import surrounded_by_hard_quotes_str, surrounded_by_soft_quotes_str


def plain_symbol_cases() -> Sequence[NameAndValue[str]]:
    return [
        NameAndValue('empty source',
                     ''
                     ),
        NameAndValue('not a plain symbol name - invalid characters',
                     NOT_A_VALID_SYMBOL_NAME
                     ),
        NameAndValue('not a plain symbol name - quoted - hard',
                     surrounded_by_hard_quotes_str(A_VALID_SYMBOL_NAME)
                     ),
        NameAndValue('not a plain symbol name - quoted - soft',
                     surrounded_by_soft_quotes_str(A_VALID_SYMBOL_NAME)
                     ),
        NameAndValue('not a plain symbol name - symbol reference',
                     symbol_reference_syntax_for_name(A_VALID_SYMBOL_NAME)
                     ),
        NameAndValue('not a plain symbol name - broken syntax due to missing end quote',
                     QUOTE_CHAR_FOR_TYPE[QuoteType.SOFT] + A_VALID_SYMBOL_NAME
                     ),
    ]


def arguments_cases() -> Sequence[NameAndValue[Sequence[ArgumentAbsStx]]]:
    return [
        NameAndValue(
            'broken argument syntax due to missing end quote / soft',
            [ArgumentOfStringAbsStx.of_str(QUOTE_CHAR_FOR_TYPE[QuoteType.SOFT] + 'argument')]
        ),
        NameAndValue(
            'broken argument syntax due to missing end quote / hard',
            [ArgumentOfStringAbsStx.of_str(QUOTE_CHAR_FOR_TYPE[QuoteType.HARD] + 'argument')]
        ),
    ]


def transformer_cases() -> Sequence[NameAndValue[StringTransformerAbsStx]]:
    return [
        NameAndValue(
            'invalid symbol reference',
            CustomStringTransformerAbsStx.of_str(NOT_A_VALID_SYMBOL_NAME_NOR_PRIMITIVE_GRAMMAR_ELEMENT_NAME)
        ),
    ]


def stdin_cases() -> Sequence[NameAndValue[StringSourceAbsStx]]:
    return [
        NameAndValue(
            'string with missing end quote',
            StringSourceOfStringAbsStx(
                str_abs_stx.StringLiteralAbsStx(
                    QUOTE_CHAR_FOR_TYPE[QuoteType.SOFT] + 'after quote'
                )
            )
        ),
    ]
