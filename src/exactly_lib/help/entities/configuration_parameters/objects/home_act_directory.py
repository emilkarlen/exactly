from exactly_lib.help.entities.configuration_parameters.contents_structure import ConfigurationParameterDocumentation
from exactly_lib.help_texts import formatting
from exactly_lib.help_texts.cross_ref.concrete_cross_refs import TestCasePhaseInstructionCrossReference
from exactly_lib.help_texts.entity import conf_params
from exactly_lib.help_texts.file_ref import REL_HOME_ACT_OPTION
from exactly_lib.help_texts.test_case.instructions.instruction_names import HOME_ACT_DIRECTORY_INSTRUCTION_NAME
from exactly_lib.help_texts.test_case.phase_names import CONFIGURATION_PHASE_NAME, \
    PHASE_NAME_DICTIONARY
from exactly_lib.test_case_file_structure.environment_variables import ENV_VAR_HOME_ACT
from exactly_lib.util.description import Description, DescriptionWithSubSections, from_simple_description
from exactly_lib.util.textformat.textformat_parser import TextParser


class _HomeActDirectoryConfigurationParameter(ConfigurationParameterDocumentation):
    def __init__(self):
        super().__init__(conf_params.HOME_ACT_DIRECTORY_CONF_PARAM_INFO)

    def purpose(self) -> DescriptionWithSubSections:
        parser = TextParser({
            'phase': PHASE_NAME_DICTIONARY,
            'the_concept': formatting.conf_param_(conf_params.HOME_ACT_DIRECTORY_CONF_PARAM_INFO),
            'home_dir_env_var': ENV_VAR_HOME_ACT,
            'rel_option': formatting.cli_option(REL_HOME_ACT_OPTION)
        })
        return from_simple_description(
            Description(self.single_line_description(),
                        parser.fnap(_REST_DESCRIPTION)))

    def see_also_targets(self) -> list:
        return [
            TestCasePhaseInstructionCrossReference(CONFIGURATION_PHASE_NAME.plain,
                                                   HOME_ACT_DIRECTORY_INSTRUCTION_NAME),
        ]


DOCUMENTATION = _HomeActDirectoryConfigurationParameter()

_REST_DESCRIPTION = """\
Instructions and phases may use files
that are supposed to exist before the test case is executed.


E.g., the {phase[act]} phase (by default) references an program that is expected
to be an executable file.

If the path to this file is relative, then it is relative the {the_concept}.


The environment variable {home_dir_env_var} contains the absolute path of this directory.


The option {rel_option} (accepted by many instructions) refers to this directory.
"""
