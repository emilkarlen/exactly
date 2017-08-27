import itertools

from exactly_lib.instructions.assert_.utils.return_pfh_via_exceptions import translate_pfh_exception_to_pfh
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.result import pfh


class Checker:
    """
    Checks a value given to the constructor,
    and returns an associated value, that may be
    propagated to the next check in a sequence of checks.

    :raises PfhException: The check is unsuccessful.
    """

    @property
    def references(self) -> list:
        return []

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              value_to_check
              ):
        raise NotImplementedError('abstract method')

    def check_and_return_pfh(self,
                             environment: InstructionEnvironmentForPostSdsStep,
                             os_services: OsServices,
                             value_to_check
                             ) -> pfh.PassOrFailOrHardError:
        return translate_pfh_exception_to_pfh(self.check,
                                              environment,
                                              os_services,
                                              value_to_check)


class SequenceOfChecks(Checker):
    """
    Executes a sequence of checks,
    by executing a sequence of :class:`Checker`s.

    Each checker returns a tuple of values that are given
    to the constructor of the next :class:`Checker`.
    """

    def __init__(self, checkers: list):
        self._checkers = tuple(checkers)
        self._references = list(itertools.chain.from_iterable([c.references for c in checkers]))

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              value_to_check):
        for checker in self._checkers:
            value_to_check = checker.check(environment, os_services, value_to_check)
        return value_to_check

    @property
    def references(self) -> list:
        return self._references
