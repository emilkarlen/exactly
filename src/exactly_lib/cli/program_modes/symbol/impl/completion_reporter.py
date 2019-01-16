from exactly_lib.cli.definitions import exit_codes
from exactly_lib.processing import exit_values
from exactly_lib.processing.standalone import result_reporting
from exactly_lib.processing.test_case_processing import AccessorError
from exactly_lib.test_case.act_phase_handling import ParseException
from exactly_lib.test_suite.file_reading.exception import SuiteSyntaxError
from exactly_lib.util.std import StdOutputFiles, file_printer_with_color_if_terminal


class CompletionReporter:
    def __init__(self,
                 output: StdOutputFiles):
        self.output = output
        self.out_printer = file_printer_with_color_if_terminal(output.out)
        self.err_printer = file_printer_with_color_if_terminal(output.err)

    def report_suite_error(self, ex: SuiteSyntaxError) -> int:
        err_only_output = StdOutputFiles(self.output.err,
                                         self.output.err)
        reporter = result_reporting.TestSuiteSyntaxErrorReporter(err_only_output)
        return reporter.report(ex)

    def report_access_error(self, error: AccessorError) -> int:
        exit_value = exit_values.from_access_error(error.error)
        self.err_printer.write_colored_line(exit_value.exit_identifier,
                                            exit_value.color)
        return exit_value.exit_code

    def report_act_phase_parse_error(self, error: ParseException) -> int:
        exit_value = exit_values.EXECUTION__VALIDATION_ERROR
        self.err_printer.write_colored_line(exit_value.exit_identifier,
                                            exit_value.color)
        return exit_value.exit_code

    def symbol_not_found(self) -> int:
        return exit_values.EXECUTION__HARD_ERROR.exit_code

    def report_success(self) -> int:
        return exit_codes.EXIT_OK
