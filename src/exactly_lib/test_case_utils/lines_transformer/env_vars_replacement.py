import pathlib
from typing import Iterable

from exactly_lib import program_info
from exactly_lib.definitions.doc_format import directory_variable_name_text
from exactly_lib.definitions.formatting import program_name
from exactly_lib.test_case_file_structure import environment_variables
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.type_system.logic import lines_transformer_values
from exactly_lib.type_system.logic.lines_transformer import LinesTransformerValue, CustomLinesTransformer
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.document import SectionContents
from exactly_lib.util.textformat.textformat_parser import TextParser

HOME_ENV_VAR_WITH_REPLACEMENT_PRECEDENCE = environment_variables.ENV_VAR_HOME_CASE


class EnvVarReplacementLinesTransformer(CustomLinesTransformer):
    def __init__(self, tcds: HomeAndSds):
        self._name_and_value_list = _derive_name_and_value_list(tcds)

    def transform(self, lines: Iterable[str]) -> Iterable[str]:
        return (_replace(self._name_and_value_list, line) for line in lines)


def value() -> LinesTransformerValue:
    return lines_transformer_values.DirDependentLinesTransformerValue(DirectoryStructurePartition,
                                                                      EnvVarReplacementLinesTransformer)


def replace(home_and_sds: HomeAndSds,
            contents: str) -> str:
    name_and_value_list = _derive_name_and_value_list(home_and_sds)
    return _replace(name_and_value_list, contents)


def _replace(name_and_value_list: list,
             contents: str) -> str:
    for var_name, var_value in name_and_value_list:
        contents = contents.replace(var_value, var_name)
    return contents


def _derive_name_and_value_list(home_and_sds: HomeAndSds) -> iter:
    hds = home_and_sds.hds
    all_vars = environment_variables.replaced(home_and_sds)
    if hds.case_dir == hds.act_dir:
        return _first_is(HOME_ENV_VAR_WITH_REPLACEMENT_PRECEDENCE, all_vars)
    elif _dir_is_sub_dir_of(hds.case_dir, hds.act_dir):
        return _first_is(environment_variables.ENV_VAR_HOME_CASE, all_vars)
    elif _dir_is_sub_dir_of(hds.act_dir, hds.case_dir):
        return _first_is(environment_variables.ENV_VAR_HOME_ACT, all_vars)
    else:
        return all_vars.items()


def _dir_is_sub_dir_of(potential_sub_dir: pathlib.Path, potential_parent_dir: pathlib.Path) -> bool:
    return str(potential_sub_dir).startswith(str(potential_parent_dir))


def _first_is(key_of_first_element: str, all_vars: dict) -> iter:
    value_of_first_element = all_vars.pop(key_of_first_element)
    return [(key_of_first_element, value_of_first_element)] + list(all_vars.items())


def with_replaced_env_vars_help() -> SectionContents:
    text_parser = TextParser({
        'checked_file': 'checked file',
        'program_name': program_info.PROGRAM_NAME,
        'home_act_env_var': environment_variables.ENV_VAR_HOME_ACT,
        'home_case_env_var': environment_variables.ENV_VAR_HOME_CASE,
        'home_env_var_with_replacement_precedence': HOME_ENV_VAR_WITH_REPLACEMENT_PRECEDENCE,
    })
    prologue = text_parser.fnap(_WITH_REPLACED_ENV_VARS_PROLOGUE)
    variables_list = [docs.simple_header_only_list(map(directory_variable_name_text,
                                                       sorted(environment_variables.ALL_REPLACED_ENV_VARS)),
                                                   docs.lists.ListType.ITEMIZED_LIST)]
    return SectionContents(prologue + variables_list)


SINGLE_LINE_DESCRIPTION = """\
Every occurrence of a string that matches the value of an {program_name} environment variable
is replaced with the name of the matching variable.
""".format(program_name=program_name(program_info.PROGRAM_NAME))

_WITH_REPLACED_ENV_VARS_PROLOGUE = """\
Variable values are replaced with variable names.


If {home_case_env_var} and {home_act_env_var} are equal, then paths will be replaced with
{home_env_var_with_replacement_precedence}.


The environment variables that are replaced are:
"""
