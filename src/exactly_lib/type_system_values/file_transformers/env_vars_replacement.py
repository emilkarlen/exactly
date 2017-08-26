import pathlib

from exactly_lib.test_case_file_structure import environment_variables
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.type_system_values.file_transformer import FileTransformer

HOME_ENV_VAR_WITH_REPLACEMENT_PRECEDENCE = environment_variables.ENV_VAR_HOME_CASE

ENV_VAR_REPLACEMENT_TRANSFORMER_NAME = 'env-var-replacement'


class EnvVarReplacementFileTransformer(FileTransformer):
    def transform(self, tcds: HomeAndSds, lines: iter) -> iter:
        name_and_value_list = _derive_name_and_value_list(tcds)
        return (_replace(name_and_value_list, line) for line in lines)


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
