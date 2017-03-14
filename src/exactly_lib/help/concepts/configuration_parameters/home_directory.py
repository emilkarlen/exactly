from exactly_lib.common.help.cross_reference_id import TestCasePhaseInstructionCrossReference
from exactly_lib.default.program_modes.test_case.default_instruction_names import HOME_DIRECTORY_INSTRUCTION_NAME
from exactly_lib.execution.environment_variables import ENV_VAR_HOME
from exactly_lib.help.concepts.contents_structure import ConfigurationParameterDocumentation
from exactly_lib.help.concepts.names_and_cross_references import HOME_DIRECTORY_CONCEPT_INFO
from exactly_lib.help.utils import formatting
from exactly_lib.help.utils.name_and_cross_ref import Name
from exactly_lib.help.utils.phase_names import phase_name_dictionary, CONFIGURATION_PHASE_NAME
from exactly_lib.test_case_file_structure.relative_path_options import REL_HOME_OPTION
from exactly_lib.util.description import Description, DescriptionWithSubSections, from_simple_description
from exactly_lib.util.textformat.parse import normalize_and_parse


class _HomeDirectoryConfigurationParameter(ConfigurationParameterDocumentation):
    def __init__(self):
        super().__init__(HOME_DIRECTORY_CONCEPT_INFO)

    def purpose(self) -> DescriptionWithSubSections:
        return from_simple_description(
            Description(self.single_line_description(),
                        normalize_and_parse(_HOME_DIRECTORY_REST_DESCRIPTION
                                            .format(phase=phase_name_dictionary(),
                                                    the_concept=_NAME.singular,
                                                    home_dir_env_var=ENV_VAR_HOME,
                                                    rel_home_option=formatting.cli_option(REL_HOME_OPTION)))))

    def default_value_str(self) -> str:
        return 'The directory where the test case file is located.'

    def _see_also_cross_refs(self) -> list:
        return [
            TestCasePhaseInstructionCrossReference(CONFIGURATION_PHASE_NAME.plain,
                                                   HOME_DIRECTORY_INSTRUCTION_NAME),
        ]


_NAME = Name('home directory', 'home directories')

HOME_DIRECTORY_CONFIGURATION_PARAMETER = _HomeDirectoryConfigurationParameter()

_HOME_DIRECTORY_REST_DESCRIPTION = """\
Instructions and phases may use predefined input in terms of files
that are supposed to exist before the test case is executed.

E.g., the {phase[act]} phase (by default) references an program that is expected
to be an executable file.


If the path to this file is relative, then it is relative the {the_concept}.


Many instructions use exiting files. E.g. for installing them into the
sandbox.


The environment variable {home_dir_env_var} contains the absolute path of this directory.


The option {rel_home_option} (accepted by many instructions) refers to this directory.
"""
