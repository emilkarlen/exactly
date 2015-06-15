from shellcheck_lib.cli.execution_mode.test_case.settings import TestCaseExecutionSettings


class MainProgram:
    def execute(self,
                command_line_arguments: list) -> int:
        raise NotImplementedError()

    def execute_test_case(self,
                          settings: TestCaseExecutionSettings) -> int:
        raise NotImplementedError()
