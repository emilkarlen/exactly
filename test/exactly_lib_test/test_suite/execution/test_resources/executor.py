import pathlib
from typing import Dict

from exactly_lib.execution import sandbox_dir_resolving
from exactly_lib.execution.configuration import PredefinedProperties
from exactly_lib.processing import processors
from exactly_lib.processing.instruction_setup import TestCaseParsingSetup
from exactly_lib.processing.parse.act_phase_source_parser import ActPhaseParser
from exactly_lib.processing.processors import TestCaseDefinition
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.test_case import os_services
from exactly_lib.test_suite import enumeration
from exactly_lib.test_suite import execution as sut
from exactly_lib.test_suite import suite_hierarchy_reading
from exactly_lib.test_suite.execution import TestCaseProcessorConstructor
from exactly_lib_test.section_document.test_resources.element_parsers import SectionElementParserThatRaisesSourceError
from exactly_lib_test.section_document.test_resources.misc import space_separator_instruction_name_extractor
from exactly_lib_test.test_suite.execution.test_resources.instruction_utils import instruction_setup
from exactly_lib_test.test_suite.test_resources.execution_utils import \
    test_case_handling_setup_with_identity_preprocessor
from exactly_lib_test.test_suite.test_resources.suite_reporting import ExecutionTracingReporterFactory


def new_executor(setup_phase_instructions: Dict[str, InstructionParser],
                 test_case_processor_constructor: TestCaseProcessorConstructor,
                 suite_root_file_path: pathlib.Path,
                 predefined_properties: PredefinedProperties) -> sut.Executor:
    test_case_definition = TestCaseDefinition(
        TestCaseParsingSetup(space_separator_instruction_name_extractor,
                             instruction_setup(setup_phase_instructions),
                             ActPhaseParser()),
        predefined_properties)
    default_configuration = processors.Configuration(test_case_definition,
                                                     test_case_handling_setup_with_identity_preprocessor(),
                                                     os_services.DEFAULT_ACT_PHASE_OS_PROCESS_EXECUTOR,
                                                     False,
                                                     sandbox_dir_resolving.mk_tmp_dir_with_prefix('test-suite-'))

    return sut.Executor(default_configuration,
                        suite_hierarchy_reading.Reader(
                            suite_hierarchy_reading.Environment(
                                SectionElementParserThatRaisesSourceError(),
                                test_case_definition.parsing_setup,
                                default_configuration.default_handling_setup)
                        ),
                        ExecutionTracingReporterFactory(),
                        enumeration.DepthFirstEnumerator(),
                        test_case_processor_constructor,
                        suite_root_file_path,
                        )
