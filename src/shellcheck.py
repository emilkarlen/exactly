"""
Main program for shellcheck
"""
import sys

from shellcheck_lib.cli.main_program_default import MainProgram


program = MainProgram(sys.stdout, sys.stderr)
exit_status = program.execute(sys.argv[1:])
sys.exit(exit_status)
