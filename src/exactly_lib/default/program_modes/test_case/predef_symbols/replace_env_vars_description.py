from exactly_lib import program_info
from exactly_lib.help_texts import instruction_arguments
from exactly_lib.test_case_file_structure import environment_variables
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure import structures as docs


def with_replaced_env_vars_help() -> list:
    format_map = {
        'checked_file': 'checked file',
        'not_option': instruction_arguments.NEGATION_ARGUMENT_STR,
        'program_name': program_info.PROGRAM_NAME,
        'home_act_env_var': environment_variables.ENV_VAR_HOME_ACT,
        'home_case_env_var': environment_variables.ENV_VAR_HOME_CASE,
        'transformation': instruction_arguments.LINES_TRANSFORMATION_ARGUMENT.name,
    }
    prologue = normalize_and_parse(_WITH_REPLACED_ENV_VARS_PROLOGUE.format(format_map))
    variables_list = [docs.simple_header_only_list(sorted(environment_variables.ALL_REPLACED_ENV_VARS),
                                                   docs.lists.ListType.VARIABLE_LIST)]
    return prologue + variables_list


_WITH_REPLACED_ENV_VARS_PROLOGUE = """\
Every occurrence of a path that matches an {program_name} environment variable
in contents of {checked_file} is replaced with the name of the matching variable.
(Variable values are replaced with variable names.)


If {home_case_env_var} and {home_act_env_var} are equal, then paths will be replaced with
{home_env_var_with_replacement_precedence}.


The environment variables that are replaced are:
"""
