from abc import ABC, abstractmethod

from exactly_lib.test_case.phases.act.adv_w_validation import AdvWValidation
from exactly_lib.test_case.phases.act.execution_input import AtcExecutionInput
from exactly_lib.test_case.phases.setup.settings_builder import SetupSettingsBuilder


class SetupSettingsHandler(ABC):
    @property
    @abstractmethod
    def builder(self) -> SetupSettingsBuilder:
        """Gives the same instance on every invokation"""
        pass

    @abstractmethod
    def as_atc_execution_input(self) -> AdvWValidation[AtcExecutionInput]:
        """Gives the contents of the handled builder, as Act Execution Input"""
        pass
