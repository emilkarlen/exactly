from abc import ABC, abstractmethod
from typing import Sequence, TypeVar, Generic, Tuple

from exactly_lib.common.report_rendering.description_tree import rendering__node_bool
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.symbol.sdv_structure import SymbolUsage, SymbolReference
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep, \
    InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.test_case.result import pfh
from exactly_lib.test_case.result import svh
from exactly_lib.type_val_deps.dep_variants.ddv import ddv_validators, ddv_validation
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.dep_variants.ddv.matcher import MatcherDdv
from exactly_lib.type_val_deps.types.matcher import MatcherSdv
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib.util.render import combinators as rend_comb
from exactly_lib.util.render.renderer import SequenceRenderer
from exactly_lib.util.simple_textstruct.structure import MinorBlock
from exactly_lib.util.symbol_table import SymbolTable

MODEL = TypeVar('MODEL')


class ModelGetter(Generic[MODEL], ABC):
    @abstractmethod
    def get(self) -> MODEL:
        """
        :raises HardErrorException
        """
        pass

    @abstractmethod
    def description(self) -> SequenceRenderer[MinorBlock]:
        pass


class ModelGetterAdv(Generic[MODEL], ABC):
    @abstractmethod
    def primitive(self, environment: ApplicationEnvironment) -> ModelGetter[MODEL]:
        pass


class ModelGetterDdv(Generic[MODEL], ABC):
    @property
    def validator(self) -> DdvValidator:
        return ddv_validation.ConstantDdvValidator.new_success()

    @abstractmethod
    def value_of_any_dependency(self, tcds: TestCaseDs) -> ModelGetterAdv[MODEL]:
        pass


class ModelGetterSdv(Generic[MODEL], ABC):
    @property
    @abstractmethod
    def references(self) -> Sequence[SymbolReference]:
        pass

    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> ModelGetterDdv[MODEL]:
        pass


class FailureMessageConfig(Generic[MODEL]):
    @abstractmethod
    def head(self, model_getter: ModelGetter[MODEL], model: MODEL) -> TextRenderer:
        pass

    @abstractmethod
    def tail(self, model_getter: ModelGetter[MODEL], model: MODEL) -> TextRenderer:
        pass


class Instruction(Generic[MODEL], AssertPhaseInstruction):
    """Makes an instruction of a :class:`Matcher`"""

    def __init__(self,
                 matcher: MatcherSdv[MODEL],
                 model_getter: ModelGetterSdv[MODEL],
                 failure_message_config: FailureMessageConfig[MODEL],
                 ):
        self._matcher = matcher
        self._model_getter = model_getter
        self._failure_message_config = failure_message_config

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return tuple(self._model_getter.references) + tuple(self._matcher.references)

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep
                         ) -> svh.SuccessOrValidationErrorOrHardError:
        _, _, validator = self._ddvs(environment.symbols)

        err_msg = validator.validate_pre_sds_if_applicable(environment.hds)
        return svh.new_maybe_svh_validation_error(err_msg)

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             settings: InstructionSettings,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        model_getter_ddv, matcher_ddv, validator = self._ddvs(environment.symbols)
        try:
            self._validate_post_setup(validator, environment.tcds)
            return self._execute(os_services, environment, model_getter_ddv, matcher_ddv)
        except HardErrorException as ex:
            return pfh.new_pfh_hard_error(ex.error)

    @staticmethod
    def _validate_post_setup(validator: DdvValidator,
                             tcds: TestCaseDs,
                             ):
        err_msg = validator.validate_post_sds_if_applicable(tcds)
        if err_msg:
            raise HardErrorException(err_msg)

    def _ddvs(self, symbols: SymbolTable) -> Tuple[ModelGetterDdv[MODEL], MatcherDdv[MODEL], DdvValidator]:
        model_getter = self._model_getter.resolve(symbols)
        matcher = self._matcher.resolve(symbols)
        return (model_getter,
                matcher,
                ddv_validators.all_of([model_getter.validator, matcher.validator]))

    def _execute(self,
                 os_services: OsServices,
                 environment: InstructionEnvironmentForPostSdsStep,
                 model_getter_ddv: ModelGetterDdv[MODEL],
                 matcher_ddv: MatcherDdv[MODEL],
                 ) -> pfh.PassOrFailOrHardError:
        tcds = environment.tcds
        app_env = ApplicationEnvironment(os_services,
                                         environment.proc_exe_settings,
                                         environment.tmp_dir__path_access.paths_access,
                                         environment.mem_buff_size)
        model_getter = model_getter_ddv.value_of_any_dependency(tcds).primitive(app_env)
        matcher = matcher_ddv.value_of_any_dependency(tcds).primitive(app_env)
        model = model_getter.get()
        result = matcher.matches_w_trace(model)

        if result.value:
            return pfh.new_pfh_pass()
        else:
            return pfh.new_pfh_fail(self._failure_message(model_getter, model, result))

    def _failure_message(self,
                         model_getter: ModelGetter[MODEL],
                         model: MODEL,
                         result: MatchingResult,
                         ) -> TextRenderer:
        return rend_comb.ConcatenationR([
            self._failure_message_config.head(model_getter, model),
            rend_comb.SingletonSequenceR(rendering__node_bool.BoolTraceRenderer(result.trace)),
            self._failure_message_config.tail(model_getter, model),
        ])
