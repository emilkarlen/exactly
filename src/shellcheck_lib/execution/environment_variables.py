import pathlib

from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure

ENV_VAR_HOME = 'SHELLCHECK_HOME'
ENV_VAR_ACT = 'SHELLCHECK_ACT'
ENV_VAR_TMP = 'SHELLCHECK_TMP'
ALL_ENV_VARS = [ENV_VAR_HOME,
                ENV_VAR_ACT,
                ENV_VAR_TMP]


def pre_eds_environment_variables(home_dir_path: pathlib.Path) -> dict:
    return {
        ENV_VAR_HOME: str(home_dir_path)
    }


def post_eds_environment_variables(eds: ExecutionDirectoryStructure) -> dict:
    return {
        ENV_VAR_ACT: str(eds.act_dir),
        ENV_VAR_TMP: str(eds.tmp_dir)
    }


def all_environment_variables(home_dir_path: pathlib.Path,
                              eds: ExecutionDirectoryStructure) -> dict:
    ret_val = pre_eds_environment_variables(home_dir_path)
    ret_val.update(post_eds_environment_variables(eds))
    return ret_val
