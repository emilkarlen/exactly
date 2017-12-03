from exactly_lib.help.entities.configuration_parameters.contents_structure import ConfigurationParameterDocumentation
from exactly_lib.help_texts import formatting
from exactly_lib.help_texts.cross_ref.concrete_cross_refs import TestCasePhaseInstructionCrossReference
from exactly_lib.help_texts.entity.conf_params import HOME_CASE_DIRECTORY_CONF_PARAM_INFO
from exactly_lib.help_texts.file_ref import REL_HOME_CASE_OPTION
from exactly_lib.help_texts.test_case.instructions.instruction_names import HOME_CASE_DIRECTORY_INSTRUCTION_NAME
from exactly_lib.help_texts.test_case.phase_names import CONFIGURATION_PHASE_NAME, \
    PHASE_NAME_DICTIONARY
from exactly_lib.test_case_file_structure.environment_variables import ENV_VAR_HOME_CASE
from exactly_lib.util.description import Description, DescriptionWithSubSections, from_simple_description
from exactly_lib.util.textformat.textformat_parser import TextParser


class _HomeCaseDirectoryConfigurationParameter(ConfigurationParameterDocumentation):
    def __init__(self):
        super().__init__(HOME_CASE_DIRECTORY_CONF_PARAM_INFO)

    def purpose(self) -> DescriptionWithSubSections:
        parser = TextParser({
            'phase': PHASE_NAME_DICTIONARY,
            'the_concept': formatting.conf_param_(HOME_CASE_DIRECTORY_CONF_PARAM_INFO),
            'home_dir_env_var': ENV_VAR_HOME_CASE,
            'rel_option': formatting.cli_option(REL_HOME_CASE_OPTION)
        })
        return from_simple_description(
            Description(self.single_line_description(),
                        parser.fnap(_REST_DESCRIPTION))
        )

    def see_also_targets(self) -> list:
        return [
            TestCasePhaseInstructionCrossReference(CONFIGURATION_PHASE_NAME.plain,
                                                   HOME_CASE_DIRECTORY_INSTRUCTION_NAME),
        ]


DOCUMENTATION = _HomeCaseDirectoryConfigurationParameter()

_REST_DESCRIPTION = """\
Instructions and phases may use predefined input in terms of files
that are supposed to exist before the test case is executed.


Many instructions use exiting files. E.g. for installing them into the
sandbox.


The environment variable {home_dir_env_var} contains the absolute path of this directory.


The option {rel_option} (accepted by many instructions) refers to this directory.
"""
