import unittest

from exactly_lib_test.default.test_resources import default_main_program_case_preprocessing
from exactly_lib_test.default.test_resources.internal_main_program_runner import \
    run_via_main_program_internally_with_default_setup
from exactly_lib_test.test_resources.main_program.main_program_check_base import tests_for_setup_with_preprocessor
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner


def suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(tests_for_setup_with_preprocessor(TESTS, main_program_runner))
    return ret_val


def suite() -> unittest.TestSuite:
    return suite_for(run_via_main_program_internally_with_default_setup())


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())

TESTS = [
    default_main_program_case_preprocessing.TransformationIntoTestCaseThatPass(),
    default_main_program_case_preprocessing.TransformationIntoTestCaseThatParserError(),
]
