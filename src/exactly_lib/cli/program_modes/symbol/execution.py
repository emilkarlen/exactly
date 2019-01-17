from typing import Tuple

from exactly_lib.cli.program_modes.symbol.impl import symbol_usage_resolving
from exactly_lib.cli.program_modes.symbol.impl.completion_reporter import CompletionReporter
from exactly_lib.cli.program_modes.symbol.impl.reports import report_environment
from exactly_lib.cli.program_modes.symbol.impl.reports.report_environment import Environment
from exactly_lib.cli.program_modes.symbol.request import SymbolInspectionRequest, RequestVariantVisitor, \
    RequestVariantList, RequestVariantIndividual
from exactly_lib.processing import test_case_processing
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.processing.processors import TestCaseDefinition
from exactly_lib.processing.standalone.accessor_resolver import AccessorResolver
from exactly_lib.processing.test_case_processing import AccessorError
from exactly_lib.section_document.section_element_parsing import SectionElementParser
from exactly_lib.test_case import test_case_doc
from exactly_lib.test_case.act_phase_handling import ParseException, ActionToCheckExecutor
from exactly_lib.test_suite.file_reading.exception import SuiteSyntaxError
from exactly_lib.util.std import StdOutputFiles


class _InvalidTestCaseError(Exception):
    def __init__(self, exit_code: int):
        self.exit_code = exit_code


class Executor:
    def __init__(self,
                 request: SymbolInspectionRequest,
                 test_case_definition: TestCaseDefinition,
                 suite_configuration_section_parser: SectionElementParser,
                 output: StdOutputFiles,
                 ):
        self.output = output
        self.suite_configuration_section_parser = suite_configuration_section_parser
        self.test_case_definition = test_case_definition
        self.request = request
        self.completion_reporter = CompletionReporter(output)

    def execute(self) -> int:
        try:
            test_case, atc_executor = self._parse()
        except _InvalidTestCaseError as ex:
            return ex.exit_code

        definitions_resolver = symbol_usage_resolving.DefinitionsInfoResolverFromTestCase(
            test_case,
            atc_executor.symbol_usages()
        )
        environment = report_environment.Environment(
            self.output,
            self.completion_reporter,
            definitions_resolver
        )

        request_handler = _RequestHandler(environment)

        return request_handler.visit(self.request.variant)

    def _parse(self) -> Tuple[test_case_doc.TestCaseOfInstructions2, ActionToCheckExecutor]:
        try:
            accessor, act_phase_setup = self._accessor()
        except SuiteSyntaxError as ex:
            raise _InvalidTestCaseError(self.completion_reporter.report_suite_error(ex))

        try:
            test_case = accessor.apply(self._test_case_file_ref())
        except AccessorError as ex:
            raise _InvalidTestCaseError(self.completion_reporter.report_access_error(ex))

        test_case_with_instructions = test_case.as_test_case_of_instructions2()
        act_phase_instructions = [
            element.value
            for element in test_case_with_instructions.act_phase
        ]
        try:
            atc_executor = act_phase_setup.atc_executor_parser.parse(act_phase_instructions)
        except ParseException as ex:
            raise _InvalidTestCaseError(self.completion_reporter.report_act_phase_parse_error(ex))

        return (test_case_with_instructions,
                atc_executor)

    def _accessor(self) -> Tuple[test_case_processing.Accessor, ActPhaseSetup]:
        case_execution_settings = self.request.case_execution_settings

        accessor_resolver = AccessorResolver(self.test_case_definition.parsing_setup,
                                             self.suite_configuration_section_parser,
                                             case_execution_settings.handling_setup)
        return accessor_resolver.resolve(case_execution_settings.test_case_file_path,
                                         case_execution_settings.run_as_part_of_explicit_suite)

    def _test_case_file_ref(self) -> test_case_processing.TestCaseFileReference:
        return test_case_processing.test_case_reference_of_source_file(
            self.request.case_execution_settings.test_case_file_path)


class _RequestHandler(RequestVariantVisitor[int]):
    def __init__(self, environment: Environment):
        self._environment = environment

    def visit_list(self, list_variant: RequestVariantList) -> int:
        from exactly_lib.cli.program_modes.symbol.impl.reports.list_all import ReportGenerator

        report_generator = ReportGenerator(self._environment)
        return report_generator.generate()

    def visit_individual(self, individual_variant: RequestVariantIndividual) -> int:
        from exactly_lib.cli.program_modes.symbol.impl.reports.individual import ReportGenerator

        report_generator = ReportGenerator(self._environment,
                                           individual_variant.name,
                                           individual_variant.list_references)
        return report_generator.generate()
