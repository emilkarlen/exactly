from exactly_lib.common.exit_value import ExitValue
from exactly_lib.common.result_reporting import output_location
from exactly_lib.test_suite.instruction_set.parse import SuiteReadError
from exactly_lib.util.std import FilePrinter


def report_suite_read_error(ex: SuiteReadError,
                            stdout_printer: FilePrinter,
                            stderr_printer: FilePrinter,
                            exit_value: ExitValue,

                            ) -> int:
    stdout_printer.write_line(exit_value.exit_identifier)
    stdout_printer.file.flush()
    output_location(stderr_printer,
                    ex.source_location,
                    ex.maybe_section_name,
                    None)
    stderr_printer.write_lines(ex.error_message_lines())
    return exit_value.exit_code
