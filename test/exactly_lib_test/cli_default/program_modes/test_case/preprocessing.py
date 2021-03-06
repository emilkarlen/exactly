import unittest

from exactly_lib_test.cli_default.program_modes.test_case.test_resources import preprocessing_tests
from exactly_lib_test.cli_default.test_resources.internal_main_program_runner import \
    main_program_runner_with_default_setup__in_same_process
from exactly_lib_test.test_resources.main_program.main_program_check_base import tests_for_setup_with_preprocessor
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner


def suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(tests_for_setup_with_preprocessor(TESTS, main_program_runner))
    return ret_val


def suite() -> unittest.TestSuite:
    return suite_for(main_program_runner_with_default_setup__in_same_process())


TESTS = [
    preprocessing_tests.TransformationIntoTestCaseThatPass(),
    preprocessing_tests.TransformationIntoTestCaseThatParserError(),
]

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
