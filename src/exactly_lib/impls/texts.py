from typing import List, Sequence

from exactly_lib.common.help import headers
from exactly_lib.definitions import misc_texts, formatting
from exactly_lib.definitions.entity import types
from exactly_lib.definitions.primitives import program
from exactly_lib.processing import exit_values
from exactly_lib.util.str_ import english_text
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser

THE_PROGRAM_TYPE_MUST_TERMINATE_SENTENCE = (
    'The {} must terminate.'.format(types.PROGRAM_TYPE_INFO.singular_name)
)

_TP = TextParser({
    'exit_code': misc_texts.EXIT_CODE,
    'HARD_ERROR': exit_values.EXECUTION__HARD_ERROR.exit_identifier,
    'ignore_exit_code_option': formatting.argument_option(program.WITH_IGNORED_EXIT_CODE_OPTION_NAME),
    'termination': THE_PROGRAM_TYPE_MUST_TERMINATE_SENTENCE,
})

OUTPUT_ON_STDERR__HEADER = 'Output on ' + misc_texts.STDERR


def run_outcome__with_ignored_exit_code_option() -> List[ParagraphItem]:
    return _TP.fnap(_RUN_WITH_IGNORED_EXIT_CODE_OPTION)


def run_description__with_ignored_exit_code_option__w_str_trans() -> List[ParagraphItem]:
    return _TP.fnap(_RUN_WITH_IGNORED_EXIT_CODE_OPTION__W_TRANSFORMATIONS)


_RUN_WITH_IGNORED_EXIT_CODE_OPTION = """\
The result is {HARD_ERROR} if the {exit_code} is non-zero,
unless {ignore_exit_code_option} is given.
"""

_RUN_WITH_IGNORED_EXIT_CODE_OPTION__W_TRANSFORMATIONS = """\
The result is {HARD_ERROR} if the {exit_code} is non-zero,
unless {ignore_exit_code_option} is given.


{termination}
"""


def type_expression_has_syntax_of_primitive(type_names: Sequence[str]) -> List[ParagraphItem]:
    types_list = english_text.and_sequence(type_names)
    return TextParser({'TYPES': types_list, 'Note': headers.NOTE_LINE_HEADER}).fnap(
        _TYPE_EXPRESSION_HAS_SYNTAX_OF_PRIMITIVE
    )


_TYPE_EXPRESSION_HAS_SYNTAX_OF_PRIMITIVE = """\
{Note} {TYPES} may not contain infix operators (unless inside parentheses).
"""
