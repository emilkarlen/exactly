from exactly_lib.processing.processors import TestCaseDefinition
from exactly_lib.processing.standalone.settings import TestCaseExecutionSettings
from exactly_lib.section_document.section_element_parsing import SectionElementParser
from exactly_lib.test_case.act_phase_handling import ActPhaseOsProcessExecutor
from exactly_lib.util.std import StdOutputFiles


def execute(settings: TestCaseExecutionSettings,
            test_case_definition: TestCaseDefinition,
            act_phase_os_process_executor_TO_REMOVE: ActPhaseOsProcessExecutor,
            suite_configuration_section_parser: SectionElementParser,
            output: StdOutputFiles,
            ) -> int:
    from exactly_lib.processing.standalone import processor
    the_processor = processor.Processor(test_case_definition,
                                        act_phase_os_process_executor_TO_REMOVE,
                                        suite_configuration_section_parser)
    return the_processor.process(output, settings)
