import unittest

from exactly_lib_test.cli.program_modes.help import argument_parsing, program_modes, entities_requests
from exactly_lib_test.cli.program_modes.help.program_modes import z_package_suite as program_modes
from exactly_lib_test.cli.program_modes.help.request_handling import z_package_suite as request_handling


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(argument_parsing.suite())
    ret_val.addTest(entities_requests.suite())
    ret_val.addTest(program_modes.suite())
    ret_val.addTest(request_handling.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
