from exactly_lib import program_info
from exactly_lib.help.concepts.configuration_parameters.home_act_directory import \
    HOME_ACT_DIRECTORY_CONFIGURATION_PARAMETER
from exactly_lib.help.concepts.configuration_parameters.home_case_directory import \
    HOME_CASE_DIRECTORY_CONFIGURATION_PARAMETER
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.help_texts.names import formatting
from exactly_lib.test_case_file_structure import sandbox_directory_structure as sds, environment_variables

_DESCRIPTION_HOME = """\
The absolute path of the {case_home_directory}.
"""

_DESCRIPTION_ACT_HOME = """\
The absolute path of the {act_home_directory}.
"""

_DESCRIPTION_ACT = """\
The absolute path of the {act_sub_dir}/ sub directory of the sandbox directory.
"""

_DESCRIPTION_TMP = """\
The absolute path of the {tmp_sub_dir}/ sub directory of the sandbox directory.
"""

_DESCRIPTION_RESULT = """\
The absolute path of the {result_sub_dir}/ sub directory of the sandbox directory.
"""

ENVIRONMENT_VARIABLES_SET_BEFORE_ACT = [
    (environment_variables.ENV_VAR_HOME_CASE, _DESCRIPTION_HOME),
    (environment_variables.ENV_VAR_HOME_ACT, _DESCRIPTION_ACT_HOME),
    (environment_variables.ENV_VAR_ACT, _DESCRIPTION_ACT),
    (environment_variables.ENV_VAR_TMP, _DESCRIPTION_TMP),

]

ENVIRONMENT_VARIABLES_SET_AFTER_ACT = [
    (environment_variables.ENV_VAR_RESULT, _DESCRIPTION_RESULT),
]


class EnvironmentVariableDescription:
    def __init__(self):
        self.text_parser = TextParser({
            'program_name': formatting.program_name(program_info.PROGRAM_NAME),
            'case_home_directory': formatting.concept(HOME_CASE_DIRECTORY_CONFIGURATION_PARAMETER.name().singular),
            'act_home_directory': formatting.concept(HOME_ACT_DIRECTORY_CONFIGURATION_PARAMETER.name().singular),
            'act_sub_dir': sds.SUB_DIRECTORY__ACT,
            'tmp_sub_dir': sds.PATH__TMP_USER,
            'result_sub_dir': sds.SUB_DIRECTORY__RESULT,
        }
        )
        self.all_variables_dict = dict(ENVIRONMENT_VARIABLES_SET_BEFORE_ACT + ENVIRONMENT_VARIABLES_SET_AFTER_ACT)

    def description_paragraphs(self, environment_variable_name: str) -> list:
        return self.text_parser.paragraph_items(self.all_variables_dict[environment_variable_name])
