import unittest

from shellcheck_lib_test.instructions.before_assert import test_resources, execute, shell


def suite():
    return unittest.TestSuite([
        test_resources.suite(),
        shell.suite(),
        execute.suite(),
    ])


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
