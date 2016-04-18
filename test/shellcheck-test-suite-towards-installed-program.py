import complete_test_suite
from shellcheck_lib_test.test_resources.cli_main_program_via_shell_utils.main_program_runner import \
    RunInstalledProgramViaOsInSubProcess

# This value is from setup.py
EXECUTABLE_NAME = 'shellcheck'

main_program_runner = RunInstalledProgramViaOsInSubProcess(EXECUTABLE_NAME)
complete_test_suite.run_suite_for(main_program_runner)
