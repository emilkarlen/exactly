from exactly_lib.cli.program_modes.symbol.completion_reporter import CompletionReporter
from exactly_lib.cli.program_modes.symbol.report_generator import ReportGenerator
from exactly_lib.processing import test_case_processing
from exactly_lib.processing.processors import TestCaseDefinition
from exactly_lib.processing.standalone.accessor_resolver import AccessorResolver
from exactly_lib.processing.standalone.settings import TestCaseExecutionSettings
from exactly_lib.processing.test_case_processing import AccessorError
from exactly_lib.section_document.section_element_parsing import SectionElementParser
from exactly_lib.test_suite.file_reading.exception import SuiteSyntaxError
from exactly_lib.util.std import StdOutputFiles


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
        self.completion_reporter = CompletionReporter(output)

    def execute(self) -> int:
        try:
            accessor = self._accessor()
        except SuiteSyntaxError as ex:
            return self.completion_reporter.report_suite_error(ex)

        try:
            test_case = accessor.apply(self._test_case_file_ref())
        except AccessorError as ex:
            return self.completion_reporter.report_access_error(ex)

        report_generator = ReportGenerator(self.output,
                                           self.completion_reporter,
                                           test_case)

        return report_generator.list()

    def _accessor(self) -> test_case_processing.Accessor:
        accessor_resolver = AccessorResolver(self.test_case_definition.parsing_setup,
                                             self.suite_configuration_section_parser,
                                             self.settings.handling_setup)
        accessor, act_phase_setup = accessor_resolver.resolve(self.settings.test_case_file_path,
                                                              self.settings.run_as_part_of_explicit_suite)
        return accessor

    def _test_case_file_ref(self) -> test_case_processing.TestCaseFileReference:
        return test_case_processing.test_case_reference_of_source_file(self.settings.test_case_file_path)
