"""
Main program for shellcheck
"""
import sys

from shellcheck_lib.cli import main_program

from shellcheck_lib.cli.default.default_main_program import MainProgram
from shellcheck_lib.cli.default import default_instructions_setup

program = MainProgram(main_program.StdOutputFiles(sys.stdout, sys.stderr),
                      default_instructions_setup.instructions_setup)
exit_status = program.execute(sys.argv[1:])
sys.exit(exit_status)
