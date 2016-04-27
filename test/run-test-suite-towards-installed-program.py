import complete_test_suite
from exactly_lib import program_info
from exactly_lib_test.test_resources.cli_main_program_via_shell_utils.main_program_runner import \
    RunInstalledProgramViaOsInSubProcess

# This value is from setup.py
EXECUTABLE_NAME = program_info.PROGRAM_NAME

main_program_runner = RunInstalledProgramViaOsInSubProcess(EXECUTABLE_NAME)
complete_test_suite.run_suite_for(main_program_runner)
