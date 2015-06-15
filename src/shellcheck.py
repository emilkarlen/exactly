"""
Main program for shellcheck
"""
import sys

from shellcheck_lib.cli import main_program
from shellcheck_lib.cli.main_program_default import MainProgram
from shellcheck_lib.cli.instruction_setup import InstructionsSetup, SingleInstructionSetup, Description
from shellcheck_lib.instructions.assert_phase import exitcode as exitcode_instruction

instructions_setup = InstructionsSetup(
    {},
    {},
    {'exitcode': SingleInstructionSetup(
        exitcode_instruction.Parser(),
        Description('Test numerical exitcode'))},
    {})

program = MainProgram(main_program.StdOutputFiles(sys.stdout, sys.stderr),
                      instructions_setup)
exit_status = program.execute(sys.argv[1:])
sys.exit(exit_status)
