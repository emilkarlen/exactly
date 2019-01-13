from exactly_lib.cli.definitions import exit_codes
from exactly_lib.processing import test_case_processing, exit_values
from exactly_lib.processing.processors import TestCaseDefinition
from exactly_lib.processing.standalone import result_reporting
from exactly_lib.processing.standalone.accessor_resolver import AccessorResolver
from exactly_lib.processing.standalone.settings import TestCaseExecutionSettings
from exactly_lib.processing.test_case_processing import AccessorError
from exactly_lib.section_document.section_element_parsing import SectionElementParser
from exactly_lib.test_case import test_case_doc
from exactly_lib.test_suite.file_reading.exception import SuiteSyntaxError
from exactly_lib.util.std import StdOutputFiles, file_printer_with_color_if_terminal


class Executor:
    def __init__(self,
                 settings: TestCaseExecutionSettings,
                 test_case_definition: TestCaseDefinition,
                 suite_configuration_section_parser: SectionElementParser,
                 output: StdOutputFiles,
                 ):
        self.output = output
        self.suite_configuration_section_parser = suite_configuration_section_parser
        self.test_case_definition = test_case_definition
        self.settings = settings
        self.reporter = _ResultReporter(output)

    def execute(self) -> int:
        try:
            accessor = self._accessor()
        except SuiteSyntaxError as ex:
            return self.reporter.report_suite_error(ex)

        try:
            test_case = accessor.apply(self._test_case_file_ref())
        except AccessorError as ex:
            return self.reporter.report_access_error(ex)

        return self._process(test_case)

    def _accessor(self) -> test_case_processing.Accessor:
        accessor_resolver = AccessorResolver(self.test_case_definition.parsing_setup,
                                             self.suite_configuration_section_parser,
                                             self.settings.handling_setup)
        accessor, act_phase_setup = accessor_resolver.resolve(self.settings.test_case_file_path,
                                                              self.settings.run_as_part_of_explicit_suite)
        return accessor

    def _test_case_file_ref(self) -> test_case_processing.TestCaseFileReference:
        return test_case_processing.test_case_reference_of_source_file(self.settings.test_case_file_path)

    def _process(self, test_case: test_case_doc.TestCase) -> int:
        return self.reporter.report_success()


class _ResultReporter:
    def __init__(self,
                 output: StdOutputFiles):
        self.output = output
        self._out_printer = file_printer_with_color_if_terminal(output.out)
        self._err_printer = file_printer_with_color_if_terminal(output.err)

    def report_suite_error(self, ex: SuiteSyntaxError) -> int:
        err_only_output = StdOutputFiles(self.output.err,
                                         self.output.err)
        reporter = result_reporting.TestSuiteSyntaxErrorReporter(err_only_output)
        return reporter.report(ex)

    def report_access_error(self, error: AccessorError) -> int:
        exit_value = exit_values.from_access_error(error.error)
        self._err_printer.write_colored_line(exit_value.exit_identifier,
                                             exit_value.color)
        return exit_value.exit_code

    def report_success(self) -> int:
        return exit_codes.EXIT_OK
