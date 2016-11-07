import unittest

from exactly_lib_test.instructions.before_assert import test_resources, change_dir, env, run, shell, new_dir, utils


def suite():
    return unittest.TestSuite([
        test_resources.suite(),
        utils.suite(),
        change_dir.suite(),
        new_dir.suite(),
        shell.suite(),
        run.suite(),
        env.suite(),
    ])


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
