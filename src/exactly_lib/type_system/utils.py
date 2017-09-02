def resolving_dependencies_from_sequence(dir_dependent_values: iter) -> set:
    """
    :rtype: Set of :class:`ResolvingDependency`
    """
    ret_val = set()
    for value in dir_dependent_values:
        ret_val.update(value.resolving_dependencies())
    return ret_val
