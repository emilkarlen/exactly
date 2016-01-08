import unittest

from shellcheck_lib_test.instructions.before_assert import test_resources, change_dir, execute, shell


def suite():
    return unittest.TestSuite([
        test_resources.suite(),
        change_dir.suite(),
        shell.suite(),
        execute.suite(),
    ])


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
