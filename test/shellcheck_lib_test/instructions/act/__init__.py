import unittest

from shellcheck_lib_test.instructions.act import test_resources


# from shellcheck_lib_test.instructions.act import executable_file


def suite():
    return unittest.TestSuite([
        test_resources.suite(),
        # executable_file.suite(),
    ])


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
