from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.assert_.utils import instruction_from_parts
from exactly_lib.instructions.multi_phase_instructions import run
from exactly_lib.processing import exit_values


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        instruction_from_parts.Parser(run.parts_parser(instruction_name)),
        run.TheInstructionDocumentation(instruction_name,
                                        single_line_description=_SINGLE_LINE_DESCRIPTION))


_SINGLE_LINE_DESCRIPTION = (
    'Runs a program, and {} if, and only if, its exit code is 0'.format(
        exit_values.EXECUTION__PASS.exit_identifier)
)
