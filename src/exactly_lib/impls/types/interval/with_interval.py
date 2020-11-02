from abc import ABC, abstractmethod

from exactly_lib.util.interval.w_inversion.interval import IntIntervalWInversion


class WithIntInterval(ABC):
    @property
    @abstractmethod
    def interval(self) -> IntIntervalWInversion:
        """
        Gives the interval that this object "applies to"
        """
        pass
