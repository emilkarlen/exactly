import unittest

from exactly_lib_test.instructions import z_package_suite as instructions
from exactly_lib_test.test_case_utils import z_package_suite as test_case_utils


def suite_that_does_not_require_main_program_runner() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    # ret_val.addTest(test_resources_test.suite())
    # ret_val.addTest(util.suite())
    # ret_val.addTest(section_document.suite())
    # ret_val.addTest(common.suite())
    # ret_val.addTest(test_case_file_structure.suite())
    # ret_val.addTest(type_system.suite())
    # ret_val.addTest(symbol.suite())
    # ret_val.addTest(test_case.suite())
    # ret_val.addTest(execution.suite())
    # ret_val.addTest(processing.suite())
    # ret_val.addTest(test_suite.suite())
    ret_val.addTest(test_case_utils.file_matcher.suite())
    ret_val.addTest(test_case_utils.files_matcher.suite())
    ret_val.addTest(instructions.assert_.contents_of_dir.suite())
    # ret_val.addTest(actors.suite())
    # ret_val.addTest(definitions.suite())
    # ret_val.addTest(help.suite())
    # ret_val.addTest(default.suite_that_does_not_require_main_program_runner())
    # ret_val.addTest(cli.suite_that_does_not_require_main_program_runner())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite_that_does_not_require_main_program_runner())
