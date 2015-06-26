"""
Main program for shellcheck
"""

from shellcheck_lib.cli.instruction_setup import InstructionsSetup, SingleInstructionSetup, Description
from shellcheck_lib.instructions.assert_phase import exitcode as exitcode_instruction

instructions_setup = InstructionsSetup(
    {},
    {},
    {'exitcode': SingleInstructionSetup(
        exitcode_instruction.Parser(),
        Description('Test numerical exitcode'))},
    {})
