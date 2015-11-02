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

from shellcheck_lib.cli.default_main_program_setup import *

exit_status = default_main_program().execute(sys.argv[1:])
sys.exit(exit_status)
