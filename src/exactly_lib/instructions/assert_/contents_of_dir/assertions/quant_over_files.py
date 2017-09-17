from exactly_lib.instructions.assert_.contents_of_dir.assertions import common
from exactly_lib.instructions.assert_.contents_of_dir.assertions.common import DirContentsAssertionPart
from exactly_lib.instructions.assert_.utils.assertion_part import AssertionPart
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.util.logic_types import Quantifier


class QuantifiedAssertion(DirContentsAssertionPart):
    def __init__(self,
                 settings: common.Settings,
                 quantifier: Quantifier,
                 actual_file_assertion_part: AssertionPart):
        super().__init__(settings, actual_file_assertion_part.validator)
        self.quantifier = quantifier
        self.actual_file_assertion_part = actual_file_assertion_part

    @property
    def references(self) -> list:
        return self._settings.file_matcher.references + self.actual_file_assertion_part.references

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              settings: common.Settings) -> common.Settings:
        return settings
