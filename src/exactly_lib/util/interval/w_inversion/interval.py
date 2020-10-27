from abc import ABC, abstractmethod

from exactly_lib.util.interval.int_interval import IntInterval


class IntIntervalWInversion(IntInterval, ABC):
    @property
    @abstractmethod
    def inversion(self) -> 'IntIntervalWInversion':
        """
        A "flexible" variant of the complement of the interval.
        In the context of matchers on integers, e.g, the inversion gives the
        interval that covers all elements that matches the negation of the matcher.

        Some instances gives a true complement of the set.
        Other instances may give an alternative interval.

        E.g. a matcher that matches integers modulo something has <unlimited> as it's interval.
        But the negation of such matcher also should give <unlimited>, since this is the set that
        covers all integers that may match the negation of the matcher.
        :return:
        """
        pass
