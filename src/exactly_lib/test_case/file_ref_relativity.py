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
