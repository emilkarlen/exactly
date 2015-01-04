__author__ = 'emil'


from shelltest_test.execution_files import test_execution_directory_structure, test_write_testcase_file

import unittest


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_execution_directory_structure.suite())
    ret_val.addTest(test_write_testcase_file.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
