from typing import Dict

from exactly_lib.tcfs import relative_path_options as rpo
from exactly_lib.tcfs.hds import HomeDs
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.tcfs.tcds import TestCaseDs

SYMBOL_HDS_CASE = rpo.REL_HDS_OPTIONS_MAP[rpo.RelHdsOptionType.REL_HDS_CASE].directory_name
SYMBOL_HDS_ACT = rpo.REL_HDS_OPTIONS_MAP[rpo.RelHdsOptionType.REL_HDS_ACT].directory_name

SYMBOL_ACT = rpo.REL_SDS_OPTIONS_MAP[rpo.RelSdsOptionType.REL_ACT].directory_name
SYMBOL_TMP = rpo.REL_SDS_OPTIONS_MAP[rpo.RelSdsOptionType.REL_TMP].directory_name
SYMBOL_RESULT = rpo.REL_SDS_OPTIONS_MAP[rpo.RelSdsOptionType.REL_RESULT].directory_name

SET_AT_SETUP__SYMBOLS = [SYMBOL_HDS_CASE,
                         SYMBOL_HDS_ACT]

SET_AT_SDS__SYMBOLS = [SYMBOL_ACT,
                       SYMBOL_TMP]

SET_AT_BEFORE_ASSERT__SYMBOLS = [SYMBOL_RESULT]

EXISTS_AT_SETUP_MAIN = SET_AT_SDS__SYMBOLS + SET_AT_SETUP__SYMBOLS

EXISTS_AT_BEFORE_ASSERT_MAIN = EXISTS_AT_SETUP_MAIN + SET_AT_BEFORE_ASSERT__SYMBOLS

ALL_REPLACED_SYMBOLS = EXISTS_AT_SETUP_MAIN


def symbols_rel_hds(hds: HomeDs) -> Dict[str, str]:
    return {
        SYMBOL_HDS_CASE: str(hds.case_dir),
        SYMBOL_HDS_ACT: str(hds.act_dir),
    }


def set_at_setup_pre_validate(hds: HomeDs) -> Dict[str, str]:
    return symbols_rel_hds(hds)


def set_at_setup_main(sds: SandboxDs) -> Dict[str, str]:
    return {
        SYMBOL_ACT: str(sds.act_dir),
        SYMBOL_TMP: str(sds.user_tmp_dir),
    }


def set_at_assert(sds: SandboxDs) -> Dict[str, str]:
    return {
        SYMBOL_RESULT: str(sds.result.root_dir),
    }


def exists_at_config() -> Dict[str, str]:
    return {}


def exists_at_setup_pre_validate(hds: HomeDs) -> Dict[str, str]:
    ret_val = exists_at_config()
    ret_val.update(set_at_setup_pre_validate(hds))
    return ret_val


def exists_at_setup_main(tcds: TestCaseDs) -> Dict[str, str]:
    ret_val = set_at_setup_pre_validate(tcds.hds)
    ret_val.update(set_at_setup_main(tcds.sds))
    return ret_val


def exists_at_assert(tcds: TestCaseDs) -> Dict[str, str]:
    ret_val = exists_at_setup_main(tcds)
    ret_val.update(set_at_assert(tcds.sds))
    return ret_val


def replaced(tcds: TestCaseDs) -> Dict[str, str]:
    """
    The environment variables that are replaced by the replace-tcds-dirs transformer.
    """
    return exists_at_setup_main(tcds)
