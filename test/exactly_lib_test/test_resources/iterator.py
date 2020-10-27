import unittest
from typing import TypeVar, Iterator

T = TypeVar('T')


class IteratorWCheckOfMaxNumRequestedElements:
    def __init__(self,
                 put: unittest.TestCase,
                 max_num_elements: int,
                 ):
        self.put = put
        self.max_num_elements = max_num_elements

    def iterator_of(self, iterator: Iterator[T]) -> Iterator[T]:
        elem_num = 0
        for elem in iterator:
            elem_num += 1
            self.put.assertLessEqual(elem_num, self.max_num_elements, 'max num elements from iterator')
            yield elem
