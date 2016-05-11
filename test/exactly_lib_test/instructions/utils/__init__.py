import unittest

from exactly_lib_test.instructions.utils import arg_parse
from exactly_lib_test.instructions.utils import executable_file, sub_process_execution
from exactly_lib_test.instructions.utils import file_properties
from exactly_lib_test.instructions.utils import file_ref


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(file_properties.suite())
    ret_val.addTest(file_ref.suite())
    ret_val.addTest(executable_file.suite())
    ret_val.addTest(sub_process_execution.suite())
    ret_val.addTest(arg_parse.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
