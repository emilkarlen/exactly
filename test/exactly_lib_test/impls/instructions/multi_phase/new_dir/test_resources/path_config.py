from typing import Sequence

from exactly_lib.impls.instructions.multi_phase import new_dir as sut
from exactly_lib.tcfs.path_relativity import RelNonHdsOptionType
from exactly_lib_test.impls.types.test_resources import relativity_options as rel_opt
from exactly_lib_test.impls.types.test_resources.relativity_options import RelativityOptionConfigurationForRelNonHds
from exactly_lib_test.tcfs.test_resources.ds_action import \
    MK_DIR_AND_CHANGE_TO_IT_INSIDE_OF_SDS_BUT_OUTSIDE_OF_ANY_OF_THE_RELATIVITY_OPTION_DIRS
from exactly_lib_test.test_resources.tcds_and_symbols.sds_env_utils import \
    mk_dir_and_change_to_it_inside_of_sds_but_outside_of_any_of_the_relativity_option_dirs

RELATIVITY_OPTIONS: Sequence[RelativityOptionConfigurationForRelNonHds] = [
    rel_opt.default_conf_rel_non_hds(RelNonHdsOptionType.REL_CWD),
    rel_opt.conf_rel_non_hds(RelNonHdsOptionType.REL_ACT),
    rel_opt.conf_rel_non_hds(RelNonHdsOptionType.REL_TMP),
    rel_opt.symbol_conf_rel_non_hds(RelNonHdsOptionType.REL_TMP,
                                    'DIR_PATH_SYMBOL',
                                    sut.RELATIVITY_VARIANTS.options.accepted_relativity_variants),
]

RELATIVITY_OPTIONS__PHASE_INTEGRATION: Sequence[RelativityOptionConfigurationForRelNonHds] = [
    rel_opt.default_conf_rel_non_hds(RelNonHdsOptionType.REL_CWD),
    rel_opt.symbol_conf_rel_non_hds(RelNonHdsOptionType.REL_TMP,
                                    'DIR_PATH_SYMBOL',
                                    sut.RELATIVITY_VARIANTS.options.accepted_relativity_variants),
]
SETUP_CWD_ACTION = mk_dir_and_change_to_it_inside_of_sds_but_outside_of_any_of_the_relativity_option_dirs()
SETUP_CWD_TO_NON_TCDS_DIR_ACTION = (
    MK_DIR_AND_CHANGE_TO_IT_INSIDE_OF_SDS_BUT_OUTSIDE_OF_ANY_OF_THE_RELATIVITY_OPTION_DIRS
)