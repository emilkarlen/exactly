from exactly_lib.test_case_file_structure import relative_path_options as rpo
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure

ENV_VAR_HOME_CASE = rpo.REL_HOME_OPTIONS_MAP[rpo.RelHomeOptionType.REL_HOME_CASE].directory_variable_name
ENV_VAR_HOME_ACT = rpo.REL_HOME_OPTIONS_MAP[rpo.RelHomeOptionType.REL_HOME_ACT].directory_variable_name

ENV_VAR_ACT = rpo.REL_SDS_OPTIONS_MAP[rpo.RelSdsOptionType.REL_ACT].directory_variable_name
ENV_VAR_TMP = rpo.REL_SDS_OPTIONS_MAP[rpo.RelSdsOptionType.REL_TMP].directory_variable_name
ENV_VAR_RESULT = rpo.REL_SDS_OPTIONS_MAP[rpo.RelSdsOptionType.REL_RESULT].directory_variable_name

SET_AT_SETUP__ENV_VARS = [ENV_VAR_HOME_CASE,
                          ENV_VAR_HOME_ACT]

SET_AT_SDS__ENV_VARS = [ENV_VAR_ACT,
                        ENV_VAR_TMP]

SET_AT_BEFORE_ASSERT__ENV_VARS = [ENV_VAR_RESULT]

ALL_ENV_VARS = SET_AT_SETUP__ENV_VARS + SET_AT_SDS__ENV_VARS + SET_AT_BEFORE_ASSERT__ENV_VARS

EXISTS_AT_SETUP_MAIN = SET_AT_SDS__ENV_VARS + SET_AT_SETUP__ENV_VARS

EXISTS_AT_BEFORE_ASSERT_MAIN = EXISTS_AT_SETUP_MAIN + SET_AT_BEFORE_ASSERT__ENV_VARS

ALL_REPLACED_ENV_VARS = EXISTS_AT_SETUP_MAIN


def env_vars_rel_home(hds: HomeDirectoryStructure) -> dict:
    return {
        ENV_VAR_HOME_CASE: str(hds.case_dir),
        ENV_VAR_HOME_ACT: str(hds.act_dir),
    }


def set_at_setup_pre_validate(hds: HomeDirectoryStructure) -> dict:
    return env_vars_rel_home(hds)


def set_at_setup_main(sds: SandboxDirectoryStructure) -> dict:
    return {
        ENV_VAR_ACT: str(sds.act_dir),
        ENV_VAR_TMP: str(sds.tmp.user_dir),
    }


def set_at_assert(sds: SandboxDirectoryStructure) -> dict:
    return {
        ENV_VAR_RESULT: str(sds.result.root_dir),
    }


def exists_at_config() -> dict:
    return {}


def exists_at_setup_pre_validate(hds: HomeDirectoryStructure) -> dict:
    ret_val = exists_at_config()
    ret_val.update(set_at_setup_pre_validate(hds))
    return ret_val


def exists_at_setup_main(home_and_sds: HomeAndSds) -> dict:
    ret_val = set_at_setup_pre_validate(home_and_sds.hds)
    ret_val.update(set_at_setup_main(home_and_sds.sds))
    return ret_val


def exists_at_assert(home_and_sds: HomeAndSds) -> dict:
    ret_val = exists_at_setup_main(home_and_sds)
    ret_val.update(set_at_assert(home_and_sds.sds))
    return ret_val


def replaced(home_and_sds: HomeAndSds) -> dict:
    """
    The environment variables that are replaced by the --with-replaced-env-vars.
    """
    return exists_at_setup_main(home_and_sds)
