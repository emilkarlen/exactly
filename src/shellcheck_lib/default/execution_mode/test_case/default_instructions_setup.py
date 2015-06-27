"""
Main program for shellcheck
"""

from shellcheck_lib.default.execution_mode.test_case.instruction_setup import InstructionsSetup, SingleInstructionSetup, \
    Description
from shellcheck_lib.instructions.assert_phase import exitcode as exitcode_instruction

instructions_setup = InstructionsSetup(
    {},
    {},
    {'exitcode': SingleInstructionSetup(
        exitcode_instruction.Parser(),
        Description('Test numerical exitcode'))},
    {})
