import unittest

from exactly_lib_test.default.program_modes import test_case, test_suite, help, html_doc
from exactly_lib_test.default.test_resources.internal_main_program_runner import \
    run_via_main_program_internally_with_default_setup
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner


def suite() -> unittest.TestSuite:
    return suite_for(run_via_main_program_internally_with_default_setup())


def suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_case.suite_for(main_program_runner))
    ret_val.addTest(test_suite.suite_for(main_program_runner))
    ret_val.addTest(help.suite_for(main_program_runner))
    ret_val.addTest(html_doc.suite_for(main_program_runner))
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
