from exactly_lib import program_info
from exactly_lib.help_texts import formatting
from exactly_lib.help_texts.entity import concepts, conf_params
from exactly_lib.test_case_file_structure import sandbox_directory_structure as sds, environment_variables
from exactly_lib.util.textformat.textformat_parser import TextParser

_DESCRIPTION_HOME = """\
The absolute path of the {case_home_directory}.
"""

_DESCRIPTION_ACT_HOME = """\
The absolute path of the {act_home_directory}.
"""

_DESCRIPTION_ACT = """\
The absolute path of the {act_sub_dir}/ sub directory of the {sandbox}.
"""

_DESCRIPTION_TMP = """\
The absolute path of the {tmp_sub_dir}/ sub directory of the {sandbox}.
"""

_DESCRIPTION_RESULT = """\
The absolute path of the {result_sub_dir}/ sub directory of the {sandbox}.
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
            'case_home_directory': formatting.conf_param_(conf_params.HOME_CASE_DIRECTORY_CONF_PARAM_INFO),
            'act_home_directory': formatting.concept_(conf_params.HOME_ACT_DIRECTORY_CONF_PARAM_INFO),
            'act_sub_dir': sds.SUB_DIRECTORY__ACT,
            'tmp_sub_dir': sds.PATH__TMP_USER,
            'result_sub_dir': sds.SUB_DIRECTORY__RESULT,
            'sandbox': formatting.concept_(concepts.SANDBOX_CONCEPT_INFO),
        }
        )
        self.all_variables_dict = dict(ENVIRONMENT_VARIABLES_SET_BEFORE_ACT + ENVIRONMENT_VARIABLES_SET_AFTER_ACT)

    def as_single_line_description_str(self, environment_variable_name: str) -> str:
        return self.text_parser.format(self.all_variables_dict[environment_variable_name])

    def as_description_paragraphs(self, environment_variable_name: str) -> list:
        return self.text_parser.paragraph_items(self.all_variables_dict[environment_variable_name])


ENVIRONMENT_VARIABLE_DESCRIPTION = EnvironmentVariableDescription()
