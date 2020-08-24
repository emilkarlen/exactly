from typing import Sequence, TypeVar, List


class FrozenSetBasedOnEquality(tuple):
    def __new__(cls, elements: Sequence):
        return tuple.__new__(cls, (tuple(_unique(elements)),))

    @property
    def elements(self) -> Sequence:
        return self[0]

    def union(self, other_set_based_on_equality):
        ret_val = list(self.elements)
        for o in other_set_based_on_equality.elements:
            if o not in self.elements:
                ret_val.append(o)
        return FrozenSetBasedOnEquality(ret_val)


T = TypeVar('T')


def _unique(elements: Sequence[T]) -> List[T]:
    ret_val = []
    for x in elements:
        if x not in ret_val:
            ret_val.append(x)
    return ret_val


def intersperse_list(element_between: T, elements: Sequence[T]) -> List[T]:
    if len(elements) <= 1:
        return list(elements)
    else:
        return [elements[0]] + [element_between] + intersperse_list(element_between, elements[1:])


def concat_list(xss: Sequence[Sequence[T]]) -> List[T]:
    ret_val = []
    for element_list in xss:
        ret_val += element_list

    return ret_val
