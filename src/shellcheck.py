###############################################################################
# Copyright (C) 2015 Emil Karlen.
#
# This file is part of shellcheck.
# 
# shellcheck is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# shellcheck is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with shellcheck.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

import sys

from shellcheck_lib.cli.default_main_program import MainProgram
from shellcheck_lib.default.execution_mode.test_case import default_instructions_setup, \
    instruction_name_and_argument_splitter
from shellcheck_lib.general.output import StdOutputFiles

program = MainProgram(StdOutputFiles(sys.stdout,
                                     sys.stderr),
                      instruction_name_and_argument_splitter.splitter,
                      default_instructions_setup.instructions_setup)
exit_status = program.execute(sys.argv[1:])
sys.exit(exit_status)
