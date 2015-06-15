from shellcheck_lib.execution import full_execution
from shellcheck_lib.cli.execution_mode.test_case.settings import Output, TestCaseExecutionSettings
from shellcheck_lib.cli.execution_mode.test_case import execution as test_case_execution
from shellcheck_lib.cli.execution_mode.help.settings import HelpSettings
from . import main_program


class MainProgram(main_program.MainProgram):
    def __init__(self,
                 output: main_program.StdOutputFiles):
        super().__init__(output)

    def execute_test_case(self, settings: TestCaseExecutionSettings) -> int:
        test_case = test_case_execution.parse_test_case_source(settings)
        script_language_setup = test_case_execution.resolve_script_language(settings)
        if settings.output is Output.ACT_PHASE_OUTPUT:
            test_case_execution.execute_act_phase(settings,
                                                  test_case,
                                                  script_language_setup)
        else:
            full_result = full_execution.execute(script_language_setup,
                                                 test_case,
                                                 settings.initial_home_dir_path,
                                                 settings.execution_directory_root_name_prefix,
                                                 settings.is_keep_execution_directory_root)
            test_case_execution.print_output_to_stdout(self._std,
                                                       settings,
                                                       full_result)
            return full_result.status.value

    def execute_help(self, settings: HelpSettings) -> int:
        return 0
