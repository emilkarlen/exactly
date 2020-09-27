from exactly_lib.tcfs.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.test_case_utils.parse.rel_opts_configuration import RelOptionArgumentConfiguration, \
    RelOptionsConfiguration

_SRC_REL_OPTIONS__BEFORE_ACT = set(RelOptionType).difference({RelOptionType.REL_RESULT})
_SRC_REL_OPTIONS__AFTER_ACT = set(RelOptionType)


def src_rel_opt_arg_conf_for_phase2(default_option: RelOptionType,
                                    src_path_argument: str,
                                    phase_is_after_act: bool,
                                    ) -> RelOptionArgumentConfiguration:
    rel_option_types = _SRC_REL_OPTIONS__AFTER_ACT if phase_is_after_act else _SRC_REL_OPTIONS__BEFORE_ACT
    return src_rel_opt_arg_conf(rel_option_types, src_path_argument, default_option)


def src_rel_opt_arg_conf(rel_option_types: set,
                         src_path_argument: str,
                         default_option: RelOptionType,
                         ) -> RelOptionArgumentConfiguration:
    return RelOptionArgumentConfiguration(
        RelOptionsConfiguration(PathRelativityVariants(
            rel_option_types,
            True),
            default_option),
        src_path_argument,
        True)
