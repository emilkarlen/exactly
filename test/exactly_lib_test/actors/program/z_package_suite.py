import unittest

from exactly_lib_test.actors.program import executable_file, shell_command, system_program, symbol_reference, \
    with_transformation, path_of_existing_file


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()

    ret_val.addTest(executable_file.suite())
    ret_val.addTest(system_program.suite())
    ret_val.addTest(shell_command.suite())
    ret_val.addTest(symbol_reference.suite())
    ret_val.addTest(with_transformation.suite())
    ret_val.addTest(path_of_existing_file.suite())

    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
