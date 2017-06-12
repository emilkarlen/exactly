import enum


class RelOptionType(enum.Enum):
    REL_ACT = 0
    REL_RESULT = 1
    REL_TMP = 2
    REL_HOME = 3
    REL_CWD = 4


class RelSdsOptionType(enum.Enum):
    """
    Id values must match those of `RelOptionType`
    """
    REL_ACT = 0
    REL_RESULT = 1
    REL_TMP = 2


class RelNonHomeOptionType(enum.Enum):
    """
    Id values must match those of `RelOptionType`
    """
    REL_ACT = 0
    REL_RESULT = 1
    REL_TMP = 2
    REL_CWD = 4


class ResolvingDependency(enum.Enum):
    HOME = 1
    NON_HOME = 2


DEPENDENCY_DICT = {
    ResolvingDependency.HOME:
        frozenset((RelOptionType.REL_HOME,)),

    ResolvingDependency.NON_HOME:
        frozenset((RelOptionType.REL_ACT,
                   RelOptionType.REL_RESULT,
                   RelOptionType.REL_TMP,
                   RelOptionType.REL_CWD,
                   )),
}

DIR_DEPENDENCY_OF = {
    RelOptionType.REL_HOME: ResolvingDependency.HOME,

    RelOptionType.REL_ACT: ResolvingDependency.NON_HOME,
    RelOptionType.REL_RESULT: ResolvingDependency.NON_HOME,
    RelOptionType.REL_TMP: ResolvingDependency.NON_HOME,
    RelOptionType.REL_CWD: ResolvingDependency.NON_HOME,
}


def rel_non_home_from_rel_sds(rel_sds: RelSdsOptionType) -> RelNonHomeOptionType:
    return RelNonHomeOptionType(rel_sds.value)


def rel_any_from_rel_sds(rel_sds: RelSdsOptionType) -> RelOptionType:
    return RelOptionType(rel_sds.value)


def rel_any_from_rel_non_home(rel_sds_or_cwd: RelNonHomeOptionType) -> RelOptionType:
    return RelOptionType(rel_sds_or_cwd.value)


class SpecificPathRelativity:
    """
    The relativity, or non-relativity, of a path.
    """

    def __init__(self, relative: RelOptionType):
        """
        :param relative: None if should denote that path is absolute
        """
        self._relative = relative

    @property
    def is_relative(self) -> bool:
        return self._relative is not None

    @property
    def is_absolute(self) -> bool:
        return self._relative is None

    @property
    def relativity_type(self) -> RelOptionType:
        """
        :rtype None: If this object denotes that the path is absolute
        """
        return self._relative


SPECIFIC_ABSOLUTE_RELATIVITY = SpecificPathRelativity(None)


def specific_relative_relativity(relativity: RelOptionType) -> SpecificPathRelativity:
    return SpecificPathRelativity(relativity)


class PathRelativityVariants(tuple):
    """
    A set of path relativities.
    """

    def __new__(cls,
                rel_option_types: set,
                absolute: bool):
        """
        :param rel_option_types: Set of `RelOptionType`
        :param absolute: absolute paths are included in the set of variants
        """
        return tuple.__new__(cls, (rel_option_types, absolute))

    @property
    def rel_option_types(self) -> set:
        """
        :return: Set of `RelOptionType`
        """
        return self[0]

    @property
    def absolute(self) -> bool:
        """
        :return: absolute paths are included in the set of variants
        """
        return self[1]
