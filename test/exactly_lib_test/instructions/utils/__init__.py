import unittest

from exactly_lib_test.instructions.utils import arg_parse
from exactly_lib_test.instructions.utils import file_properties
from exactly_lib_test.instructions.utils import file_ref
from exactly_lib_test.instructions.utils import sub_process_execution


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(file_properties.suite())
    ret_val.addTest(file_ref.suite())
    ret_val.addTest(sub_process_execution.suite())
    ret_val.addTest(arg_parse.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
