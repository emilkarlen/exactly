import enum


class RelOptionType(enum.Enum):
    REL_ACT = 0
    REL_RESULT = 1
    REL_TMP = 2
    REL_HOME = 3
    REL_CWD = 4


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
