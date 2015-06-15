"""
Main program for shellcheck
"""
import sys

from shellcheck_lib.cli import main_program
from shellcheck_lib.cli.main_program_default import MainProgram


program = MainProgram(main_program.StdOutputFiles(sys.stdout, sys.stderr))
exit_status = program.execute(sys.argv[1:])
sys.exit(exit_status)
