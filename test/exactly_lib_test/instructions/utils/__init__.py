import unittest

from exactly_lib_test.instructions.utils import executable_file, sub_process_execution
from exactly_lib_test.instructions.utils import file_properties
from exactly_lib_test.instructions.utils import file_ref, parse_file_ref, parse_here_document, parse_utils


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(parse_utils.suite())
    ret_val.addTest(file_properties.suite())
    ret_val.addTest(file_ref.suite())
    ret_val.addTest(parse_file_ref.suite())
    ret_val.addTest(parse_here_document.suite())
    ret_val.addTest(executable_file.suite())
    ret_val.addTest(sub_process_execution.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
