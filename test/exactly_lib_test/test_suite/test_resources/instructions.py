from exactly_lib.test_suite.instruction_set.sections.configuration.instruction_definition import \
    ConfigurationSectionInstruction, ConfigurationSectionEnvironment
from exactly_lib_test.test_resources.actions import do_nothing


def configuration_section_instruction_that(do_execute=do_nothing) -> ConfigurationSectionInstruction:
    return _ConfigurationSectionInstructionThat(do_execute=do_execute)


class _ConfigurationSectionInstructionThat(ConfigurationSectionInstruction):
    def __init__(self, do_execute):
        self.do_execute = do_execute

    def execute(self, environment: ConfigurationSectionEnvironment):
        self.do_execute(environment)
