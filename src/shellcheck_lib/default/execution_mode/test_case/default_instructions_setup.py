"""
Main program for shellcheck
"""

from shellcheck_lib.default.execution_mode.test_case.instruction_setup import InstructionsSetup, \
    SingleInstructionSetup
from shellcheck_lib.instructions.assert_phase import exitcode as exitcode_instruction
from shellcheck_lib.instructions.assert_phase import file as file_instruction
from shellcheck_lib.instructions.assert_phase import stdout_stderr as stdout_stderr_instruction

instructions_setup = InstructionsSetup(
    {},
    {},
    {
        'exitcode':
            SingleInstructionSetup(
                exitcode_instruction.Parser(),
                exitcode_instruction.DESCRIPTION),
        'file':
            SingleInstructionSetup(
                file_instruction.Parser(),
                file_instruction.DESCRIPTION),
        'stdout':
            SingleInstructionSetup(
                stdout_stderr_instruction.ParserForContentsForStdout(),
                stdout_stderr_instruction.description('stdout')),
        'stderr':
            SingleInstructionSetup(
                stdout_stderr_instruction.ParserForContentsForStderr(),
                stdout_stderr_instruction.description('stderr')),
    },
    {})
