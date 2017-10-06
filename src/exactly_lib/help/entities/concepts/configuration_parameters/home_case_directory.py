from exactly_lib.help.entities.concepts.contents_structure import ConfigurationParameterDocumentation
from exactly_lib.help_texts.cross_reference_id import TestCasePhaseInstructionCrossReference
from exactly_lib.help_texts.entity.concepts import HOME_CASE_DIRECTORY_CONCEPT_INFO
from exactly_lib.help_texts.file_ref import REL_HOME_CASE_OPTION
from exactly_lib.help_texts.names import formatting
from exactly_lib.help_texts.test_case.instructions.instruction_names import HOME_CASE_DIRECTORY_INSTRUCTION_NAME
from exactly_lib.help_texts.test_case.phase_names import phase_name_dictionary, CONFIGURATION_PHASE_NAME
from exactly_lib.test_case_file_structure.environment_variables import ENV_VAR_HOME_CASE
from exactly_lib.util.description import Description, DescriptionWithSubSections, from_simple_description
from exactly_lib.util.textformat.parse import normalize_and_parse


class _HomeCaseDirectoryConfigurationParameter(ConfigurationParameterDocumentation):
    def __init__(self):
        super().__init__(HOME_CASE_DIRECTORY_CONCEPT_INFO)

    def purpose(self) -> DescriptionWithSubSections:
        return from_simple_description(
            Description(self.single_line_description(),
                        normalize_and_parse(
                            _REST_DESCRIPTION
                                .format(phase=phase_name_dictionary(),
                                        the_concept=HOME_CASE_DIRECTORY_CONCEPT_INFO.singular_name,
                                        home_dir_env_var=ENV_VAR_HOME_CASE,
                                        rel_option=formatting.cli_option(REL_HOME_CASE_OPTION)))))

    def default_value_str(self) -> str:
        return 'The directory where the test case file is located.'

    def see_also_targets(self) -> list:
        return [
            TestCasePhaseInstructionCrossReference(CONFIGURATION_PHASE_NAME.plain,
                                                   HOME_CASE_DIRECTORY_INSTRUCTION_NAME),
        ]


HOME_CASE_DIRECTORY_CONFIGURATION_PARAMETER = _HomeCaseDirectoryConfigurationParameter()

_REST_DESCRIPTION = """\
Instructions and phases may use predefined input in terms of files
that are supposed to exist before the test case is executed.


Many instructions use exiting files. E.g. for installing them into the
sandbox.


The environment variable {home_dir_env_var} contains the absolute path of this directory.


The option {rel_option} (accepted by many instructions) refers to this directory.
"""
