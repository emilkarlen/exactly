from typing import List

from exactly_lib.definitions import misc_texts, formatting
from exactly_lib.definitions.entity import types, syntax_elements
from exactly_lib.definitions.primitives import program
from exactly_lib.processing import exit_values
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
    'PROGRAM': syntax_elements.PROGRAM_SYNTAX_ELEMENT.singular_name,
    'program': types.PROGRAM_TYPE_INFO.name,
    'string_transformer': types.STRING_TRANSFORMER_TYPE_INFO.name,
    'NOTE': misc_texts.NOTE_LINE_HEADER,
})

OUTPUT_ON_STDERR__HEADER = 'Output on ' + misc_texts.STDERR


def run_with_ignored_exit_code_option() -> List[ParagraphItem]:
    return _TP.fnap(_RUN_WITH_IGNORED_EXIT_CODE_OPTION)


def run_with_ignored_exit_code_option__w_str_trans() -> List[ParagraphItem]:
    return _TP.fnap(_RUN_WITH_IGNORED_EXIT_CODE_OPTION__W_TRANSFORMATIONS)


_RUN_WITH_IGNORED_EXIT_CODE_OPTION = """\
The result is {HARD_ERROR} if the {exit_code} is non-zero,
unless {ignore_exit_code_option} is given.


{termination}
"""

_RUN_WITH_IGNORED_EXIT_CODE_OPTION__W_TRANSFORMATIONS = """\
The result is {HARD_ERROR} if the {exit_code} is non-zero,
unless {ignore_exit_code_option} is given.


({NOTE} {ignore_exit_code_option} do not apply to {program:s} run by
{string_transformer:s} applied via {PROGRAM}.)


{termination}
"""
