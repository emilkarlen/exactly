from typing import Sequence, Set

from exactly_lib.tcfs.path_relativity import RelHdsOptionType, RelSdsOptionType, RelNonHdsOptionType, RelOptionType, \
    PathRelativityVariants
from exactly_lib_test.impls.types.test_resources.relativity_options import conf_rel_hds, conf_rel_sds, conf_rel_non_hds, \
    default_conf_rel_non_hds, RelativityOptionConfiguration, default_conf_rel_hds

ALLOWED_SRC_FILE_RELATIVITIES__BEFORE_ACT = [
    conf_rel_hds(RelHdsOptionType.REL_HDS_CASE),
    conf_rel_hds(RelHdsOptionType.REL_HDS_ACT),
    conf_rel_sds(RelSdsOptionType.REL_ACT),
    conf_rel_sds(RelSdsOptionType.REL_TMP),
    conf_rel_non_hds(RelNonHdsOptionType.REL_CWD),
    default_conf_rel_hds(RelHdsOptionType.REL_HDS_CASE),
]

DISALLOWED_DST_RELATIVITIES = [
    RelOptionType.REL_RESULT,
    RelOptionType.REL_HDS_CASE,
    RelOptionType.REL_HDS_ACT,
]

ARBITRARY_ALLOWED_SRC_FILE_RELATIVITY = conf_rel_non_hds(RelNonHdsOptionType.REL_TMP)
ARBITRARY_ALLOWED_DST_FILE_RELATIVITY = conf_rel_non_hds(RelNonHdsOptionType.REL_TMP)

ALLOWED_DST_FILE_RELATIVITIES = [
    conf_rel_non_hds(RelNonHdsOptionType.REL_ACT),
    conf_rel_non_hds(RelNonHdsOptionType.REL_TMP),
    conf_rel_non_hds(RelNonHdsOptionType.REL_CWD),
    default_conf_rel_non_hds(RelNonHdsOptionType.REL_CWD),

]

ACCEPTED_DST_RELATIVITY_VARIANTS = PathRelativityVariants(
    {RelOptionType.REL_ACT,
     RelOptionType.REL_TMP,
     RelOptionType.REL_CWD},
    absolute=False,
)


def accepted_src_file_relativities(phase_is_after_act: bool) -> Sequence[RelativityOptionConfiguration]:
    return (
        ALLOWED_SRC_FILE_RELATIVITIES__BEFORE_ACT + [conf_rel_sds(RelSdsOptionType.REL_RESULT)]
        if phase_is_after_act
        else
        ALLOWED_SRC_FILE_RELATIVITIES__BEFORE_ACT
    )


def accepted_non_hds_source_relativities(phase_is_after_act: bool) -> Set[RelNonHdsOptionType]:
    if phase_is_after_act:
        return set(RelNonHdsOptionType)
    else:
        return set(RelNonHdsOptionType).difference({RelNonHdsOptionType.REL_RESULT})
