from exactly_lib_test.test_resources.main_program import main_program_check_for_test_suite
from exactly_lib_test.test_suite.reporters.test_resources import simple_progress_reporter_output


class SetupWithReplacementOfVariableOutputWithPlaceholders(
    main_program_check_for_test_suite.SetupWithoutPreprocessorWithTestActor):
    def _translate_actual_stdout_before_assertion(self, output_on_stdout: str) -> str:
        return simple_progress_reporter_output.replace_variable_output_with_placeholders(output_on_stdout)
