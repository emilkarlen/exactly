from exactly_lib.act_phase_setups import command_line
from exactly_lib.test_suite.instruction_set.sections.configuration.instruction_definition import \
    ConfigurationSectionEnvironment
from exactly_lib_test.processing.processing_utils import PreprocessorThat


def configuration_section_environment() -> ConfigurationSectionEnvironment:
    def f():
        pass

    return ConfigurationSectionEnvironment(PreprocessorThat(f),
                                           command_line.act_phase_setup())
