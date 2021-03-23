from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.tcfs.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.type_val_deps.types.path.rel_opts_configuration import RelOptionsConfiguration, \
    RelOptionArgumentConfiguration

RELATIVITIES__READ__BEFORE_ACT = frozenset(set(RelOptionType).difference({RelOptionType.REL_RESULT}))
RELATIVITIES__READ__AFTER_ACT = frozenset(set(RelOptionType))

RELATIVITY_VARIANTS__READ__BEFORE_ACT = PathRelativityVariants.of_frozen_set(RELATIVITIES__READ__BEFORE_ACT, True)
RELATIVITY_VARIANTS__READ__AFTER_ACT = PathRelativityVariants.of_frozen_set(RELATIVITIES__READ__AFTER_ACT, True)


def relativity_variants(phase_is_after_act: bool) -> PathRelativityVariants:
    return (
        RELATIVITY_VARIANTS__READ__AFTER_ACT
        if phase_is_after_act
        else
        RELATIVITY_VARIANTS__READ__BEFORE_ACT
    )


ALL_REL_OPTIONS = set(RelOptionType) - {RelOptionType.REL_RESULT}
ALL_HDS_REL_OPTIONS = {RelOptionType.REL_HDS_CASE, RelOptionType.REL_HDS_ACT}

ALL_REL_OPTION_VARIANTS = PathRelativityVariants(ALL_REL_OPTIONS, True)

PATH_ASSERTION_RELATIVITIES = PathRelativityVariants(
    ALL_REL_OPTIONS,
    True)

PATH_ASSERTION_REL_OPTS_CONF = RelOptionsConfiguration(PATH_ASSERTION_RELATIVITIES,
                                                       RelOptionType.REL_CWD)


def all_rel_options_config(default: RelOptionType) -> RelOptionsConfiguration:
    return RelOptionsConfiguration(PathRelativityVariants(ALL_REL_OPTIONS,
                                                          True),
                                   default)


REL_OPTIONS_CONFIGURATION = all_rel_options_config(RelOptionType.REL_HDS_CASE)

HDS_AND_ABS_RELATIVITY_VARIANTS = PathRelativityVariants(
    ALL_HDS_REL_OPTIONS,
    True)


def all_rel_options_arg_config(argument_syntax_name: str,
                               path_suffix_is_required: bool = True,
                               default: RelOptionType = RelOptionType.REL_HDS_CASE) -> RelOptionArgumentConfiguration:
    return RelOptionArgumentConfiguration(all_rel_options_config(default),
                                          argument_syntax_name,
                                          path_suffix_is_required)


def argument_config__read(argument_syntax_name: str,
                          phase_is_after_act: bool,
                          default: RelOptionType) -> RelOptionArgumentConfiguration:
    return RelOptionArgumentConfiguration(
        RelOptionsConfiguration(
            relativity_variants(phase_is_after_act),
            default,
        ),
        argument_syntax_name,
        path_suffix_is_required=True)


ALL_REL_OPTIONS_ARG_CONFIG = all_rel_options_arg_config(syntax_elements.PATH_SYNTAX_ELEMENT.singular_name)
