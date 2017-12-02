def distribute_width(column_content_widths: list, available_width: int) -> list:
    """
    Distributes the given width among the given columns.

    Width will be distributed evenly. But columns that need less width will be
    assigned their minimum needed width (so that the table will be as narrow
    as possible).

    If width cannot be distributed evenly (because available width is not evenly dividable),
    then columns at the beginning will be assigned one more unit of width.

    :param column_content_widths: The maximum needed with for each column.
    :param available_width: Total available width for all columns.
    :returns [int]
    """
    distribution = _initial_distribution(column_content_widths, available_width)
    superfluous_width, unsatisfied_columns = _shrink_and_get_superfluous_width(distribution)
    while unsatisfied_columns and superfluous_width > 0:
        _widen_by_distributing_superfluous_width(superfluous_width, unsatisfied_columns)
        superfluous_width, unsatisfied_columns = _shrink_and_get_superfluous_width(unsatisfied_columns)
    return [ci.assigned_width for ci in distribution]


class _ColumnInfo:
    def __init__(self,
                 contents_width: int,
                 assigned_width: int):
        self.contents_width = contents_width
        self.assigned_width = assigned_width

    def is_satisfied(self) -> bool:
        return self.contents_width <= self.assigned_width

    def shrink_to_minimum_for_satisfaction_and_give_away_superfluous(self) -> int:
        superfluous = self.assigned_width - self.contents_width
        if superfluous > 0:
            self.assigned_width = self.contents_width
            return superfluous
        else:
            return 0

    def grow(self, width: int):
        self.assigned_width += width


def _shrink_and_get_superfluous_width(column_infos: list) -> (int, list):
    superfluous_width = 0
    unsatisfied_columns = []
    for ci in column_infos:
        superfluous_width += ci.shrink_to_minimum_for_satisfaction_and_give_away_superfluous()
        if not ci.is_satisfied():
            unsatisfied_columns.append(ci)
    return superfluous_width, unsatisfied_columns


def _widen_by_distributing_superfluous_width(superfluous_width: int, accepting_columns: list):
    num_cols = len(accepting_columns)
    base_growth, num_cols_that_will_grow_one_more = divmod(superfluous_width, num_cols)
    growth_distribution = ((num_cols_that_will_grow_one_more * [base_growth + 1]) +
                           ((num_cols - num_cols_that_will_grow_one_more) * [base_growth]))
    for growth, col in zip(growth_distribution, accepting_columns):
        col.grow(growth)


def _initial_distribution(column_content_widths: list, available_width: int) -> list:
    base, remainder = divmod(available_width, len(column_content_widths))
    ret_val = []
    for content_width in column_content_widths:
        assigned_width = base
        if remainder > 0:
            assigned_width += 1
            remainder -= 1
        ret_val.append(_ColumnInfo(content_width, assigned_width))
    return ret_val
