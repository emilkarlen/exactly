class FrozenSetBasedOnEquality(tuple):
    def __new__(cls,
                elements: list):
        return tuple.__new__(cls, (tuple(_unique(elements)),))

    @property
    def elements(self) -> tuple:
        return self[0]

    def union(self, other_set_based_on_equality):
        ret_val = list(self.elements)
        for o in other_set_based_on_equality.elements:
            if o not in self.elements:
                ret_val.append(o)
        return FrozenSetBasedOnEquality(ret_val)


def _unique(elements: list) -> list:
    ret_val = []
    for x in elements:
        if x not in ret_val:
            ret_val.append(x)
    return ret_val
