from typing import Dict

from exactly_lib.test_case_file_structure import relative_path_options as rpo
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.test_case_file_structure.tcds import Tcds

ENV_VAR_HDS_CASE = rpo.REL_HDS_OPTIONS_MAP[rpo.RelHdsOptionType.REL_HDS_CASE].directory_variable_name
ENV_VAR_HDS_ACT = rpo.REL_HDS_OPTIONS_MAP[rpo.RelHdsOptionType.REL_HDS_ACT].directory_variable_name

ENV_VAR_ACT = rpo.REL_SDS_OPTIONS_MAP[rpo.RelSdsOptionType.REL_ACT].directory_variable_name
ENV_VAR_TMP = rpo.REL_SDS_OPTIONS_MAP[rpo.RelSdsOptionType.REL_TMP].directory_variable_name
ENV_VAR_RESULT = rpo.REL_SDS_OPTIONS_MAP[rpo.RelSdsOptionType.REL_RESULT].directory_variable_name

SET_AT_SETUP__ENV_VARS = [ENV_VAR_HDS_CASE,
                          ENV_VAR_HDS_ACT]

SET_AT_SDS__ENV_VARS = [ENV_VAR_ACT,
                        ENV_VAR_TMP]

SET_AT_BEFORE_ASSERT__ENV_VARS = [ENV_VAR_RESULT]

ALL_ENV_VARS = SET_AT_SETUP__ENV_VARS + SET_AT_SDS__ENV_VARS + SET_AT_BEFORE_ASSERT__ENV_VARS

EXISTS_AT_SETUP_MAIN = SET_AT_SDS__ENV_VARS + SET_AT_SETUP__ENV_VARS

EXISTS_AT_BEFORE_ASSERT_MAIN = EXISTS_AT_SETUP_MAIN + SET_AT_BEFORE_ASSERT__ENV_VARS

ALL_REPLACED_ENV_VARS = EXISTS_AT_SETUP_MAIN


def env_vars_rel_hds(hds: HomeDirectoryStructure) -> Dict[str, str]:
    return {
        ENV_VAR_HDS_CASE: str(hds.case_dir),
        ENV_VAR_HDS_ACT: str(hds.act_dir),
    }


def set_at_setup_pre_validate(hds: HomeDirectoryStructure) -> Dict[str, str]:
    return env_vars_rel_hds(hds)


def set_at_setup_main(sds: SandboxDirectoryStructure) -> Dict[str, str]:
    return {
        ENV_VAR_ACT: str(sds.act_dir),
        ENV_VAR_TMP: str(sds.user_tmp_dir),
    }


def set_at_assert(sds: SandboxDirectoryStructure) -> Dict[str, str]:
    return {
        ENV_VAR_RESULT: str(sds.result.root_dir),
    }


def exists_at_config() -> Dict[str, str]:
    return {}


def exists_at_setup_pre_validate(hds: HomeDirectoryStructure) -> Dict[str, str]:
    ret_val = exists_at_config()
    ret_val.update(set_at_setup_pre_validate(hds))
    return ret_val


def exists_at_setup_main(tcds: Tcds) -> Dict[str, str]:
    ret_val = set_at_setup_pre_validate(tcds.hds)
    ret_val.update(set_at_setup_main(tcds.sds))
    return ret_val


def exists_at_assert(tcds: Tcds) -> Dict[str, str]:
    ret_val = exists_at_setup_main(tcds)
    ret_val.update(set_at_assert(tcds.sds))
    return ret_val


def replaced(tcds: Tcds) -> Dict[str, str]:
    """
    The environment variables that are replaced by the REPLACE_TEST_CASE_DIRS transformer.
    """
    return exists_at_setup_main(tcds)
