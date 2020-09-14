"""
Executes the (default) main program.

Tests use this file to execute the main program, which uses the fact that this file
is located in the root directory of the source - making it possible to import modules
from the library without having to set the sys.path.
"""
import sys

from exactly_lib.cli_default.default_main_program_setup import main

exit_status = main()
sys.exit(exit_status)
