from exactly_lib.common.process_result_reporter import ProcessResultReporter, Environment
from exactly_lib.test_suite import exit_values
from exactly_lib.test_suite import reporting
from exactly_lib.test_suite.file_reading.exception import SuiteReadError


class SuiteReadErrorReporter(ProcessResultReporter):
    def __init__(self,
                 ex: SuiteReadError,
                 suite_processing_reporter: reporting.RootSuiteProcessingReporter
                 ):
        self._ex = ex
        self._suite_processing_reporter = suite_processing_reporter

    def report(self, environment: Environment) -> int:
        from exactly_lib.test_suite import error_reporting

        exit_value = exit_values.INVALID_SUITE
        self._suite_processing_reporter.report_invalid_suite(exit_value, environment)
        environment.std_files.out.flush()

        error_reporting.print_suite_read_error(self._ex, environment.std_file_printers.err)

        return exit_value.exit_code
