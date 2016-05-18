from exactly_lib.act_phase_setups import single_command_setup
from exactly_lib.test_suite.instruction_set.sections.configuration.instruction_definition import \
    ConfigurationSectionEnvironment
from exactly_lib_test.test_case.processing_utils import PreprocessorThat


def configuration_section_environment() -> ConfigurationSectionEnvironment:
    def f():
        pass

    return ConfigurationSectionEnvironment(PreprocessorThat(f),
                                           single_command_setup.act_phase_setup())
