from exactly_lib.instructions.assert_.contents_of_dir.assertions import common
from exactly_lib.instructions.assert_.utils.assertion_part import AssertionPart
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, \
    InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.result import svh
from exactly_lib.util.logic_types import Quantifier


class InstructionForQuantifiedAssertion(common._InstructionBase):
    def __init__(self,
                 settings: common.Settings,
                 quantifier: Quantifier,
                 actual_file_assertion_part: AssertionPart,
                 ):
        """
        :param actual_file_assertion_part: An assertion part on a :class:`FileToCheck`
        """
        super().__init__(settings)
        self.quantifier = quantifier
        self._actual_file_assertion_part = actual_file_assertion_part
        self._symbol_usages = settings.path_to_check.references + settings.file_matcher.references

    def symbol_usages(self) -> list:
        return self._symbol_usages

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def _main_after_checking_existence_of_dir(self, environment: InstructionEnvironmentForPostSdsStep):
        pass
