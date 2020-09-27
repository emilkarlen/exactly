import enum
from typing import Set, Optional


class RelOptionType(enum.Enum):
    REL_CWD = 0

    REL_HDS_CASE = 1
    REL_HDS_ACT = 2

    REL_ACT = 3
    REL_TMP = 4
    REL_RESULT = 5


class RelSdsOptionType(enum.Enum):
    """
    Denotes directories in the Sandbox Directory Structure.

    Id values must match those of `RelOptionType`
    """
    REL_ACT = 3
    REL_TMP = 4
    REL_RESULT = 5


class RelNonHdsOptionType(enum.Enum):
    """
    Denotes directories not in the Home Directory Structure.

    Id values must match those of `RelOptionType`
    """
    REL_CWD = 0

    REL_ACT = 3
    REL_TMP = 4
    REL_RESULT = 5


class RelHdsOptionType(enum.Enum):
    """
    Denotes directories in the Home Directory Structure.

    Id values must match those of `RelOptionType`
    """
    REL_HDS_CASE = 1
    REL_HDS_ACT = 2


class DirectoryStructurePartition(enum.Enum):
    HDS = 1
    NON_HDS = 2


DEPENDENCY_DICT = {
    DirectoryStructurePartition.HDS:
        frozenset((RelOptionType.REL_HDS_CASE,
                   RelOptionType.REL_HDS_ACT)),

    DirectoryStructurePartition.NON_HDS:
        frozenset((RelOptionType.REL_ACT,
                   RelOptionType.REL_RESULT,
                   RelOptionType.REL_TMP,
                   RelOptionType.REL_CWD,
                   )),
}

RESOLVING_DEPENDENCY_OF = {
    RelOptionType.REL_HDS_CASE: DirectoryStructurePartition.HDS,
    RelOptionType.REL_HDS_ACT: DirectoryStructurePartition.HDS,

    RelOptionType.REL_ACT: DirectoryStructurePartition.NON_HDS,
    RelOptionType.REL_RESULT: DirectoryStructurePartition.NON_HDS,
    RelOptionType.REL_TMP: DirectoryStructurePartition.NON_HDS,
    RelOptionType.REL_CWD: DirectoryStructurePartition.NON_HDS,
}


def rel_non_hds_from_rel_sds(rel_sds: RelSdsOptionType) -> RelNonHdsOptionType:
    return RelNonHdsOptionType(rel_sds.value)


def rel_any_from_rel_sds(rel_sds: RelSdsOptionType) -> RelOptionType:
    return RelOptionType(rel_sds.value)


def rel_any_from_rel_non_hds(rel_sds_or_cwd: RelNonHdsOptionType) -> RelOptionType:
    return RelOptionType(rel_sds_or_cwd.value)


def rel_any_from_rel_hds(rel_hds: RelHdsOptionType) -> RelOptionType:
    return RelOptionType(rel_hds.value)


def rel_hds_from_rel_any(rel_any: RelOptionType) -> RelHdsOptionType:
    """
    :return: None iff rel_any is not relative one of the HDS directories
    """
    try:
        return RelHdsOptionType(rel_any.value)
    except ValueError:
        return None


def rel_sds_from_rel_any(rel_any: RelOptionType) -> RelSdsOptionType:
    """
    :return: None iff rel_any is not relative one of the sandbox directories
    """
    try:
        return RelSdsOptionType(rel_any.value)
    except ValueError:
        return None


class SpecificPathRelativity:
    """
    The relativity, or non-relativity, of a path.
    """

    def __init__(self, relative: Optional[RelOptionType]):
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
    def relativity_type(self) -> Optional[RelOptionType]:
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
                rel_option_types: Set[RelOptionType],
                absolute: bool):
        """
        :param absolute: absolute paths are included in the set of variants
        """
        return tuple.__new__(cls, (rel_option_types, absolute))

    @property
    def rel_option_types(self) -> Set[RelOptionType]:
        return self[0]

    @property
    def absolute(self) -> bool:
        """
        :return: absolute paths are included in the set of variants
        """
        return self[1]
