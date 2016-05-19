import unittest

from exactly_lib_test import act_phase_setups
from exactly_lib_test import cli
from exactly_lib_test import default
from exactly_lib_test import execution
from exactly_lib_test import help
from exactly_lib_test import instructions
from exactly_lib_test import processing
from exactly_lib_test import section_document
from exactly_lib_test import test_case
from exactly_lib_test import test_suite
from exactly_lib_test import util


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(util.suite())
    ret_val.addTest(section_document.suite())
    ret_val.addTest(test_case.suite())
    ret_val.addTest(execution.suite())
    ret_val.addTest(processing.suite())
    ret_val.addTest(cli.suite())
    ret_val.addTest(test_suite.suite())
    ret_val.addTest(instructions.suite())
    ret_val.addTest(act_phase_setups.suite())
    ret_val.addTest(help.suite())
    ret_val.addTest(default.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
