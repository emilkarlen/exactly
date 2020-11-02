from typing import Sequence

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.definitions import misc_texts, formatting
from exactly_lib.definitions.entity import types
from exactly_lib.impls.instructions.assert_.utils import instruction_from_parts
from exactly_lib.impls.instructions.multi_phase import run
from exactly_lib.impls.instructions.multi_phase.utils import run_assertions
from exactly_lib.processing import exit_values
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        instruction_from_parts.Parser(run.parts_parser(instruction_name)),
        run.TheInstructionDocumentation(instruction_name,
                                        single_line_description=_get_single_line_description(),
                                        outcome=_get_outcome,
                                        ))


def _get_single_line_description() -> str:
    return _TP.format(_SINGLE_LINE_DESCRIPTION)


def _get_outcome() -> Sequence[ParagraphItem]:
    return _TP.fnap(_OUTCOME)


_TP = TextParser({
    'program_type': types.PROGRAM_TYPE_INFO.name,
    'PASS': exit_values.EXECUTION__PASS.exit_identifier,
    'FAIL': exit_values.EXECUTION__FAIL.exit_identifier,
    'exit_code': misc_texts.EXIT_CODE,
    'ignore_exit_code_option': formatting.argument_option(run.IGNORE_EXIT_CODE_OPTION_NAME),
})

_SINGLE_LINE_DESCRIPTION = run_assertions.single_line_description_as_assertion('Runs {program_type:a/q}')

_OUTCOME = """\
{PASS} if the {exit_code} is zero,
or {ignore_exit_code_option} is given.

Otherwise {FAIL}.
"""
