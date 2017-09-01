from exactly_lib_test.common.test_resources.instruction_setup import single_instruction_setup
from exactly_lib_test.test_suite.test_resources.instructions import configuration_section_instruction_that

CONFIGURATION_SECTION_INSTRUCTIONS = {
    'test-suite-conf-instruction': single_instruction_setup('test-suite-conf-instruction',
                                                            configuration_section_instruction_that()),
}
