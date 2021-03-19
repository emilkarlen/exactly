from exactly_lib.tcfs.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.type_val_deps.types.path.rel_opts_configuration import RelOptionsConfiguration

RELATIVITIES__ALL = frozenset(set(RelOptionType))
RELATIVITIES__EXCEPT_RESULT = frozenset(set(RelOptionType).difference({RelOptionType.REL_RESULT}))

RELATIVITY_VARIANTS__READ__BEFORE_ACT = PathRelativityVariants.of_frozen_set(
    RELATIVITIES__EXCEPT_RESULT,
    True
)

RELATIVITY_VARIANTS__READ__AFTER_ACT = PathRelativityVariants.of_frozen_set(
    RELATIVITIES__ALL,
    True
)


def relativity_variants__read(phase_is_after_act: bool) -> PathRelativityVariants:
    return (
        RELATIVITY_VARIANTS__READ__AFTER_ACT
        if phase_is_after_act
        else
        RELATIVITY_VARIANTS__READ__BEFORE_ACT
    )


def relativity_configuration__read(default_option: RelOptionType,
                                   phase_is_after_act: bool) -> RelOptionsConfiguration:
    return RelOptionsConfiguration(relativity_variants__read(phase_is_after_act),
                                   default_option)
