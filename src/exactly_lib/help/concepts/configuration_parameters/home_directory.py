from exactly_lib.execution.environment_variables import ENV_VAR_HOME
from exactly_lib.help.concepts.concept_structure import ConfigurationParameterDocumentation, Name
from exactly_lib.help.utils.description import Description
from exactly_lib.help.utils.phase_names import phase_name_dictionary
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure.structures import text


class _HomeDirectoryConfigurationParameter(ConfigurationParameterDocumentation):
    def __init__(self):
        super().__init__(Name('home directory', 'home directories'))

    def purpose(self) -> Description:
        return Description(text(_HOME_DIRECTORY_SINGLE_LINE_DESCRIPTION),
                           normalize_and_parse(_HOME_DIRECTORY_REST_DESCRIPTION
                                               .format(phase=phase_name_dictionary(),
                                                       home_dir_env_var=ENV_VAR_HOME)))

    def default_value_str(self) -> str:
        return 'The directory where the test case file is located.'


HOME_DIRECTORY_CONFIGURATION_PARAMETER = _HomeDirectoryConfigurationParameter()
_HOME_DIRECTORY_SINGLE_LINE_DESCRIPTION = """\
Default location of (external, existing) files referenced from the test case."""
_HOME_DIRECTORY_REST_DESCRIPTION = """\
TODO (improve description!)

Instructions and phases may use predefined input in terms of files
that are supposed to exist before the test case is executed.

E.g., the {phase[act]} phase (by default) references an program that is expected
to be an executable file.


If the path to this file is relative, then it is relative the Home Directory.


Many instructions use exiting files. E.g. for installing them into the
sandbox.


The environment variable {home_dir_env_var} contains the absolute path of this directory.
"""