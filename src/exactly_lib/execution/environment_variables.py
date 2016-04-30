import pathlib

from exactly_lib.execution.execution_directory_structure import ExecutionDirectoryStructure

ENV_VAR_HOME = 'EXACTLY_HOME'
ENV_VAR_ACT = 'EXACTLY_ACT'
ENV_VAR_TMP = 'EXACTLY_TMP'
ENV_VAR_RESULT = 'EXACTLY_RESULT'

SET_AT_SETUP__ENV_VARS = [ENV_VAR_HOME]
SET_AT_EDS__ENV_VARS = [ENV_VAR_ACT,
                        ENV_VAR_TMP]
SET_AT_BEFORE_ASSERT__ENV_VARS = [ENV_VAR_RESULT]

ALL_ENV_VARS = SET_AT_SETUP__ENV_VARS + SET_AT_EDS__ENV_VARS + SET_AT_BEFORE_ASSERT__ENV_VARS

EXISTS_AT_SETUP_MAIN = SET_AT_EDS__ENV_VARS + SET_AT_SETUP__ENV_VARS

EXISTS_AT_BEFORE_ASSERT_MAIN = EXISTS_AT_SETUP_MAIN + SET_AT_BEFORE_ASSERT__ENV_VARS

ALL_REPLACED_ENV_VARS = EXISTS_AT_SETUP_MAIN


def set_at_setup_pre_validate(home_dir_path: pathlib.Path) -> dict:
    return {
        ENV_VAR_HOME: str(home_dir_path),
    }


def set_at_setup_main(eds: ExecutionDirectoryStructure) -> dict:
    return {
        ENV_VAR_ACT: str(eds.act_dir),
        ENV_VAR_TMP: str(eds.tmp.user_dir),
    }


def set_at_assert(eds: ExecutionDirectoryStructure) -> dict:
    return {
        ENV_VAR_RESULT: str(eds.result.root_dir),
    }


def exists_at_config() -> dict:
    return {}


def exists_at_setup_pre_validate(home_dir_path: pathlib.Path) -> dict:
    ret_val = exists_at_config()
    ret_val.update(set_at_setup_pre_validate(home_dir_path))
    return ret_val


def exists_at_setup_main(home_dir_path: pathlib.Path,
                         eds: ExecutionDirectoryStructure) -> dict:
    ret_val = set_at_setup_pre_validate(home_dir_path)
    ret_val.update(set_at_setup_main(eds))
    return ret_val


def exists_at_assert(home_dir_path: pathlib.Path,
                     eds: ExecutionDirectoryStructure) -> dict:
    ret_val = exists_at_setup_main(home_dir_path, eds)
    ret_val.update(set_at_assert(eds))
    return ret_val


def replaced(home_dir_path: pathlib.Path,
             eds: ExecutionDirectoryStructure) -> dict:
    """
    The environment variables that are replaced by the --with-replaced-env-vars.
    """
    return exists_at_setup_main(home_dir_path, eds)
