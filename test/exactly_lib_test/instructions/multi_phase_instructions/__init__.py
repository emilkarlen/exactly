import unittest

from exactly_lib_test.instructions.multi_phase_instructions import \
    test_resources_test, utils, \
    new_dir, change_dir, \
    run, run_tests_of_instruction_embryo, \
    new_file, env, shell


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        test_resources_test.suite(),
        utils.suite(),
        new_dir.suite(),
        change_dir.suite(),
        new_file.suite(),
        run.suite(),
        run_tests_of_instruction_embryo.suite(),
        env.suite(),
        shell.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
