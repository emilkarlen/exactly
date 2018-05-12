from exactly_lib.common.exit_value import ExitValue
from exactly_lib.util.ansi_terminal_color import ForegroundColor

ALL_PASS = ExitValue(0, 'OK', ForegroundColor.GREEN)
INVALID_SUITE = ExitValue(3, 'INVALID_SUITE', ForegroundColor.YELLOW)
FAILED_TESTS = ExitValue(4, 'ERROR', ForegroundColor.RED)
