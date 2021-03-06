import unittest

from exactly_lib_test.cli_default.program_modes.help import main_help, test_case, test_suite, html_doc, \
    predefined_content_parts
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner


def suite_that_does_not_require_main_program_runner() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(html_doc.suite_that_does_not_require_main_program_runner())
    return ret_val


def suite_that_does_require_main_program_runner(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(main_help.suite_that_does_require_main_program_runner(main_program_runner))
    ret_val.addTest(test_case.suite_that_does_require_main_program_runner(main_program_runner))
    ret_val.addTest(test_suite.suite_that_does_require_main_program_runner(main_program_runner))
    ret_val.addTest(html_doc.suite_that_does_require_main_program_runner(main_program_runner))
    ret_val.addTest(predefined_content_parts.suite_that_does_require_main_program_runner(main_program_runner))
    return ret_val


def complete_suite_for(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    ret_val = suite_that_does_not_require_main_program_runner()
    ret_val.addTests(suite_that_does_require_main_program_runner(main_program_runner))
    return ret_val


def _run_complete():
    from exactly_lib_test.cli_default.test_resources.internal_main_program_runner import \
        main_program_runner_with_default_setup__in_same_process

    unittest.TextTestRunner().run(complete_suite_for(main_program_runner_with_default_setup__in_same_process()))


if __name__ == '__main__':
    _run_complete()
