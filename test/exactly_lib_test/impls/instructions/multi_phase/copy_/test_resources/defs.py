from exactly_lib.tcfs.path_relativity import RelOptionType, PathRelativityVariants, DEPENDENCY_DICT, \
    DirectoryStructurePartition, RelHdsOptionType, RelNonHdsOptionType
from exactly_lib_test.impls.types.test_resources import relativity_options as rel_opt_conf


def path_relativity_variants__src(phase_is_after_act: bool) -> PathRelativityVariants:
    rel_opts = set(RelOptionType)
    if not phase_is_after_act:
        rel_opts.remove(RelOptionType.REL_RESULT)

    return PathRelativityVariants(rel_opts, True)


PATH_RELATIVITY_VARIANTS__DST = PathRelativityVariants(
    DEPENDENCY_DICT[DirectoryStructurePartition.NON_HDS] - {RelOptionType.REL_RESULT},
    False,
)
ARBITRARY_LEGAL_RELATIVITY__SRC = RelOptionType.REL_HDS_CASE
ARBITRARY_LEGAL_RELATIVITY__SRC__HDS = RelHdsOptionType.REL_HDS_CASE
ARBITRARY_LEGAL_RELATIVITY__DST = RelOptionType.REL_ACT
ARBITRARY_LEGAL_RELATIVITY__DST__NON_HDS = RelNonHdsOptionType.REL_ACT
ARBITRARY_SRC_REL_OPT = rel_opt_conf.conf_rel_hds(RelHdsOptionType.REL_HDS_ACT)
ARBITRARY_DST_REL_OPT = rel_opt_conf.conf_rel_non_hds(RelNonHdsOptionType.REL_ACT)
DEFAULT_SRC_REL_OPT = rel_opt_conf.default_conf_rel_hds(RelHdsOptionType.REL_HDS_CASE)
DEFAULT_DST_REL_OPT = rel_opt_conf.default_conf_rel_non_hds(RelNonHdsOptionType.REL_CWD)
