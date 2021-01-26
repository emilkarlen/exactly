import unittest

from exactly_lib_test.impls.actors.program import executable_file, shell_command, system_program, symbol_reference, \
    with_transformation, path_of_existing_file, program_with_defined_stdin


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()

    ret_val.addTest(executable_file.suite())
    ret_val.addTest(system_program.suite())
    ret_val.addTest(shell_command.suite())
    ret_val.addTest(symbol_reference.suite())
    ret_val.addTest(with_transformation.suite())
    ret_val.addTest(path_of_existing_file.suite())
    ret_val.addTest(program_with_defined_stdin.suite())

    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
