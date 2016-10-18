import unittest

from exactly_lib_test.instructions.act import test_resources


def suite() -> unittest.TestCase:
    return test_resources.suite()


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
