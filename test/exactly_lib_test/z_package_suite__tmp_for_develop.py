import unittest

from exactly_lib_test.default import z_package_suite as default

from exactly_lib_test.actors import z_package_suite as actors
from exactly_lib_test.execution import z_package_suite as execution
from exactly_lib_test.processing import z_package_suite as processing
from exactly_lib_test.symbol import z_package_suite as symbol
from exactly_lib_test.test_case import z_package_suite as test_case
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner
from exactly_lib_test.test_resources_test import z_package_suite as test_resources_test
from exactly_lib_test.test_suite import z_package_suite as test_suite
from exactly_lib_test.type_val_prims import z_package_suite as type_system


def suite_that_does_not_require_main_program_runner() -> unittest.TestSuite:
    from exactly_lib_test.cli import z_package_suite as cli
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources_test.suite())
    #ret_val.addTest(util.suite())
    #ret_val.addTest(section_document.suite())
    #ret_val.addTest(common.suite())
    #ret_val.addTest(test_case_file_structure.suite())
    ret_val.addTest(type_system.suite())
    ret_val.addTest(symbol.suite())
    ret_val.addTest(test_case.suite())
    ret_val.addTest(execution.suite())
    ret_val.addTest(processing.suite())
    ret_val.addTest(test_suite.suite())
    #ret_val.addTest(test_case_utils.suite())
    #ret_val.addTest(instructions.suite())
    ret_val.addTest(actors.suite())
    #ret_val.addTest(definitions.suite())
    #ret_val.addTest(help.suite())
    ret_val.addTest(default.suite_that_does_not_require_main_program_runner())
    ret_val.addTest(cli.suite_that_does_not_require_main_program_runner())
    return ret_val


def suite_that_does_require_any_main_program_runner(mpr: MainProgramRunner) -> unittest.TestSuite:
    from exactly_lib_test.cli import z_package_suite as cli
    ret_val = unittest.TestSuite()
    ret_val.addTest(default.suite_that_does_require_main_program_runner(mpr))
    ret_val.addTest(cli.suite_that_does_require_main_program_runner(mpr))
    return ret_val


def suite_that_does_require_main_program_runner_with_default_setup(
        mpr: MainProgramRunner) -> unittest.TestSuite:
    return default.suite_that_does_require_main_program_runner_with_default_setup(mpr)


def complete_without_main_program_runner() -> unittest.TestSuite:
    return suite_that_does_not_require_main_program_runner()


def complete_with_any_main_program_runner(mpr: MainProgramRunner) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(complete_without_main_program_runner())
    ret_val.addTest(suite_that_does_require_any_main_program_runner(mpr))
    return ret_val


def complete_with_main_program_runner_with_default_setup(mpr: MainProgramRunner) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(complete_with_any_main_program_runner(mpr))
    ret_val.addTest(suite_that_does_require_main_program_runner_with_default_setup(mpr))
    return ret_val


def just_with_main_program_runner_with_default_setup(mpr: MainProgramRunner) -> unittest.TestSuite:
    return suite_that_does_require_main_program_runner_with_default_setup(mpr)


if __name__ == '__main__':
    from exactly_lib_test.default.test_resources.internal_main_program_runner import \
        main_program_runner_with_default_setup__in_same_process

    unittest.TextTestRunner().run(
        complete_with_main_program_runner_with_default_setup(
            main_program_runner_with_default_setup__in_same_process()))
