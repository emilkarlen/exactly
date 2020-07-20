from typing import Sequence

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.definitions import misc_texts, formatting
from exactly_lib.definitions.entity import types
from exactly_lib.instructions.assert_.utils import instruction_from_parts
from exactly_lib.instructions.multi_phase import run
from exactly_lib.processing import exit_values
from exactly_lib.test_case_utils.documentation import texts
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        instruction_from_parts.Parser(run.parts_parser(instruction_name)),
        run.TheInstructionDocumentation(instruction_name,
                                        single_line_description=_get_single_line_description(),
                                        description_rest=_get_description_rest,
                                        ))


def _get_single_line_description() -> str:
    return _TP.format(_SINGLE_LINE_DESCRIPTION)


def _get_description_rest() -> Sequence[ParagraphItem]:
    return _TP.fnap(_DESCRIPTION_REST)


_TP = TextParser({
    'program_type': types.PROGRAM_TYPE_INFO.name,
    'PASS': exit_values.EXECUTION__PASS.exit_identifier,
    'FAIL': exit_values.EXECUTION__FAIL.exit_identifier,
    'exit_code': misc_texts.EXIT_CODE,
    'ignore_exit_code_option': formatting.argument_option(run.IGNORE_EXIT_CODE_OPTION_NAME),
    'termination': texts.THE_PROGRAM_TYPE_MUST_TERMINATE_SENTENCE,
})

_SINGLE_LINE_DESCRIPTION = 'Runs {program_type:a/q}, and {PASS} or {FAIL} depending on its {exit_code}'

_DESCRIPTION_REST = """\
{PASS} if the {exit_code} is zero,
or {ignore_exit_code_option} is given.

Otherwise, {FAIL}.


{termination}
"""
