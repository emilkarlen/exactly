import unittest

from exactly_lib_test.cli.program_modes.help import argument_parsing, program_modes, entities_requests


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(argument_parsing.suite())
    ret_val.addTest(entities_requests.suite())
    ret_val.addTest(program_modes.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
