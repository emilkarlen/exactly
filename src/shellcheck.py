"""
Main program for shellcheck
"""
import sys

from shellcheck_lib.cli.main_program_default import MainProgram


MainProgram().execute(sys.argv[1:])
