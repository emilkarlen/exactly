import unittest

from exactly_lib_test.instructions.multi_phase_instructions import new_dir, change_dir, run, new_file, env, shell


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        new_dir.suite(),
        change_dir.suite(),
        new_file.suite(),
        run.suite(),
        env.suite(),
        shell.suite(),
    ])


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
