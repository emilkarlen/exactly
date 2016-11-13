from exactly_lib.common.exit_value import ExitValue

ALL_PASS = ExitValue(0, 'OK')
INVALID_SUITE = ExitValue(3, 'INVALID_SUITE')
FAILED_TESTS = ExitValue(4, 'ERROR')
