"""
Main program for shellcheck
"""
import sys

from shellcheck_lib.default.default_main_program import MainProgram
from shellcheck_lib.default.execution_mode.test_case import default_instructions_setup, \
    instruction_name_and_argument_splitter
from shellcheck_lib.general.output import StdOutputFiles

program = MainProgram(StdOutputFiles(sys.stdout,
                                     sys.stderr),
                      instruction_name_and_argument_splitter.splitter,
                      default_instructions_setup.instructions_setup)
exit_status = program.execute(sys.argv[1:])
sys.exit(exit_status)
