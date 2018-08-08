import unittest

from exactly_lib_test.cli.program_modes.test_case import \
    argument_parsing, source_file_paths, hds_dir_initialization, env_var_initialization, \
    config_from_suite, keep_sandbox
from exactly_lib_test.test_resources.main_program.main_program_runner import MainProgramRunner


def suite_that_does_not_require_main_program_runner() -> unittest.TestSuite:
    return unittest.TestSuite([
        argument_parsing.suite(),
        source_file_paths.suite(),
        hds_dir_initialization.suite(),
        env_var_initialization.suite(),
        keep_sandbox.suite(),
        config_from_suite.suite_that_does_not_require_main_program_runner(),
    ])


def suite_that_does_require_main_program_runner(main_program_runner: MainProgramRunner) -> unittest.TestSuite:
    return config_from_suite.suite_that_does_require_main_program_runner(main_program_runner)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite_that_does_not_require_main_program_runner())
