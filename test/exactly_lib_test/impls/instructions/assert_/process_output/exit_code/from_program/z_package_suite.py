import unittest

from exactly_lib_test.impls.instructions.assert_.process_output.exit_code.from_program import validation, \
    full_execution, stdin, other_proc_exe_env, invalid_syntax, transformations, execute_program_once, \
    hard_error_from_command_executor


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        invalid_syntax.suite(),
        validation.suite(),
        stdin.suite(),
        other_proc_exe_env.suite(),
        transformations.suite(),
        hard_error_from_command_executor.suite(),
        full_execution.suite(),
        execute_program_once.suite()
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
