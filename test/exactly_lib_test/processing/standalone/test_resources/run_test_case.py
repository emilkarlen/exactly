from pathlib import Path
from typing import Optional

from exactly_lib.cli.test_suite_def import TestSuiteDefinition
from exactly_lib.execution.configuration import PredefinedProperties
from exactly_lib.impls.os_services import os_services_access
from exactly_lib.processing.instruction_setup import TestCaseParsingSetup
from exactly_lib.processing.processors import TestCaseDefinition
from exactly_lib.processing.standalone import processor as sut
from exactly_lib.processing.standalone.settings import TestCaseExecutionSettings, ReportingOption
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib_test.appl_env.test_resources.command_executors import CommandExecutorThatJustReturnsConstant
from exactly_lib_test.processing.standalone.test_resources import instructions_inclusion_test_base as base
from exactly_lib_test.processing.standalone.test_resources.run_processor import capture_output_from_processor
from exactly_lib_test.test_resources.process import SubProcessResult


class TestCaseRunner(base.TestCaseRunner):
    def run(self,
            parsing_setup: TestCaseParsingSetup,
            test_case_handling_setup: TestCaseHandlingSetup,
            test_suite_definition: TestSuiteDefinition,
            case_file: Path,
            explicit_suite_file_path: Optional[Path]) -> SubProcessResult:
        processor = sut.Processor(TestCaseDefinition(parsing_setup,
                                                     PredefinedProperties.new_empty()),
                                  os_services_access.new_for_cmd_exe(
                                      CommandExecutorThatJustReturnsConstant()
                                  ),
                                  test_suite_definition.configuration_section_parser)

        execution_settings = TestCaseExecutionSettings(case_file,
                                                       case_file.parent,
                                                       ReportingOption.STATUS_CODE,
                                                       test_case_handling_setup,
                                                       run_as_part_of_explicit_suite=explicit_suite_file_path)
        return capture_output_from_processor(processor,
                                             execution_settings)
