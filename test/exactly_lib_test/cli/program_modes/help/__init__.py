import unittest

from exactly_lib_test.cli.program_modes.help import argument_parsing, concepts, actors


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(argument_parsing.suite())
    ret_val.addTest(concepts.suite())
    ret_val.addTest(actors.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
