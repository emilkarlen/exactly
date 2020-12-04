from typing import AbstractSet

from exactly_lib.impls.types.path.rel_opts_configuration import RelOptionArgumentConfiguration, \
    RelOptionsConfiguration
from exactly_lib.tcfs.path_relativity import RelOptionType, PathRelativityVariants

_SRC_REL_OPTIONS__AFTER_ACT = set(RelOptionType)
_SRC_REL_OPTIONS__BEFORE_ACT = _SRC_REL_OPTIONS__AFTER_ACT.difference({RelOptionType.REL_RESULT})


def rel_opts_for_phase(phase_is_after_act: bool) -> AbstractSet[RelOptionType]:
    return _SRC_REL_OPTIONS__AFTER_ACT if phase_is_after_act else _SRC_REL_OPTIONS__BEFORE_ACT


def src_rel_opt_arg_conf_for_phase(default_option: RelOptionType,
                                   src_path_argument: str,
                                   phase_is_after_act: bool,
                                   ) -> RelOptionArgumentConfiguration:
    return src_rel_opt_arg_conf(rel_opts_for_phase(phase_is_after_act),
                                src_path_argument,
                                default_option)


def src_rel_opt_conf_for_phase(default_option: RelOptionType,
                               phase_is_after_act: bool,
                               ) -> RelOptionsConfiguration:
    return src_rel_opt_conf(rel_opts_for_phase(phase_is_after_act), default_option)


def src_rel_opt_arg_conf(rel_option_types: AbstractSet[RelOptionType],
                         src_path_argument: str,
                         default_option: RelOptionType,
                         ) -> RelOptionArgumentConfiguration:
    return RelOptionArgumentConfiguration(
        src_rel_opt_conf(rel_option_types, default_option),
        src_path_argument,
        True)


def src_rel_opt_conf(rel_option_types: AbstractSet[RelOptionType],
                     default_option: RelOptionType,
                     ) -> RelOptionsConfiguration:
    return RelOptionsConfiguration(PathRelativityVariants(
        set(rel_option_types),
        True),
        default_option)
