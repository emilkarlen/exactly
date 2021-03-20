import unittest
from contextlib import contextmanager
from typing import TypeVar, Generic, Callable, ContextManager

from exactly_lib.common.report_rendering import print_
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.type_val_deps.dep_variants.adv.app_env_dep_val import ApplicationEnvironmentDependentValue
from exactly_lib.type_val_deps.dep_variants.ddv.full_deps.ddv import FullDepsDdv
from exactly_lib.type_val_deps.dep_variants.sdv.full_deps.resolving_environment import FullResolvingEnvironment
from exactly_lib.type_val_deps.dep_variants.sdv.full_deps.sdv import FullDepsSdv
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import Arrangement, AssertionResolvingEnvironment, \
    ExecutionExpectation
from exactly_lib_test.tcfs.test_resources.ds_construction import tcds_with_act_as_curr_dir_3
from exactly_lib_test.tcfs.test_resources.fake_ds import fake_tcds
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion, AssertionBase, MessageBuilder, \
    StopAssertion
from exactly_lib_test.type_val_deps.dep_variants.full_deps.test_resources.common_properties_checker import PRIMITIVE, \
    INPUT, OUTPUT, Applier, CommonExecutionPropertiesChecker
from exactly_lib_test.util.file_utils.test_resources import tmp_file_spaces


class ExecutionAssertion(AssertionBase[FullDepsSdv[PRIMITIVE]]):
    FAKE_TCDS = fake_tcds()

    def __init__(self,
                 model_constructor: INPUT,
                 arrangement: Arrangement,
                 adv: Callable[[AssertionResolvingEnvironment],
                               Assertion[ApplicationEnvironmentDependentValue[PRIMITIVE]]],
                 primitive: Callable[[AssertionResolvingEnvironment], Assertion[PRIMITIVE]],
                 execution: ExecutionExpectation[OUTPUT],
                 applier: Applier[PRIMITIVE, INPUT, OUTPUT],
                 common_properties:
                 CommonExecutionPropertiesChecker[PRIMITIVE, OUTPUT],
                 check_application_result_with_tcds: bool,
                 ):
        self.model_constructor = model_constructor
        self.applier = applier
        self.arrangement = arrangement
        self.adv = adv
        self.primitive = primitive
        self.execution = execution
        self.common_properties = common_properties
        self.check_application_result_with_tcds = check_application_result_with_tcds

    def _apply(self,
               put: unittest.TestCase,
               value: FullDepsSdv[PRIMITIVE],
               message_builder: MessageBuilder,
               ):
        execution_checker = ExecutionChecker(
            put,
            self.model_constructor,
            self.arrangement,
            self.adv,
            self.primitive,
            self.execution,
            self.applier,
            self.common_properties,
            self.check_application_result_with_tcds,
            message_builder,
        )

        execution_checker.check(value)


_T = TypeVar('_T')


class _ValueAssertionApplier:
    def __init__(self,
                 assertion: Assertion[_T],
                 value: _T,
                 message_builder: asrt.MessageBuilder,
                 ):
        self.assertion = assertion
        self.value = value
        self.message_builder = message_builder

    def apply(self, put: unittest.TestCase):
        self.assertion.apply(put, self.value, self.message_builder)


class ExecutionChecker(Generic[PRIMITIVE, INPUT, OUTPUT]):
    FAKE_TCDS = fake_tcds()

    def __init__(self,
                 put: unittest.TestCase,
                 model_constructor: INPUT,
                 arrangement: Arrangement,
                 adv: Callable[[AssertionResolvingEnvironment],
                               Assertion[ApplicationEnvironmentDependentValue[PRIMITIVE]]],
                 primitive: Callable[[AssertionResolvingEnvironment], Assertion[PRIMITIVE]],
                 execution: ExecutionExpectation[OUTPUT],
                 applier: Applier[PRIMITIVE, INPUT, OUTPUT],
                 common_properties:
                 CommonExecutionPropertiesChecker[PRIMITIVE, OUTPUT],
                 check_application_result_with_tcds: bool,
                 message_builder: MessageBuilder = MessageBuilder(),
                 ):
        self.put = put
        self.model_constructor = model_constructor
        self.applier = applier
        self.arrangement = arrangement
        self.adv = adv
        self.primitive = primitive
        self.execution = execution
        self.common_properties = common_properties
        self.check_application_result_with_tcds = check_application_result_with_tcds
        self.message_builder = message_builder

        self.hds = None
        self.tcds = None

    def check(self, sut: FullDepsSdv[PRIMITIVE]):
        try:
            self._check(sut)
        except StopAssertion:
            pass

    def _check(self, sut: FullDepsSdv[PRIMITIVE]):
        message_builder = self.message_builder.for_sub_component('ddv')
        matcher_ddv = self._resolve_ddv(sut, message_builder)

        self.common_properties.check_ddv(
            self.put,
            matcher_ddv,
            message_builder,
        )

        with self._tcds_with_act_as_curr_dir() as tcds:
            self.hds = tcds.hds

            self._check_with_hds(matcher_ddv, message_builder)

            self.tcds = tcds

            application_result_assertion = self._check_with_sds(matcher_ddv, message_builder)

            if self.check_application_result_with_tcds:
                application_result_assertion.apply(self.put)

        if not self.check_application_result_with_tcds:
            application_result_assertion.apply(self.put)

    def _tcds_with_act_as_curr_dir(self) -> ContextManager[TestCaseDs]:
        tcds_arrangement = self.arrangement.tcds
        return (
            tcds_with_act_as_curr_dir_3(tcds_arrangement)
            if tcds_arrangement
            else
            self._dummy_tcds_setup()
        )

    @contextmanager
    def _dummy_tcds_setup(self) -> ContextManager[TestCaseDs]:
        yield self.FAKE_TCDS

    def _check_with_hds(self,
                        ddv: FullDepsDdv[PRIMITIVE],
                        message_builder: MessageBuilder):
        self._check_validation_pre_sds(ddv, message_builder)

    def _check_with_sds(self,
                        ddv: FullDepsDdv[PRIMITIVE],
                        message_builder__ddv: MessageBuilder) -> _ValueAssertionApplier:
        self._check_validation_post_sds(ddv, message_builder__ddv)

        full_resolving_env = FullResolvingEnvironment(
            self.arrangement.symbols,
            self.tcds,
            ApplicationEnvironment(
                self.arrangement.process_execution.os_services,
                self.arrangement.process_execution.process_execution_settings,
                tmp_file_spaces.tmp_dir_file_space_for_test(
                    self.tcds.sds.internal_tmp_dir / 'application-tmp-dir'),
                self.arrangement.mem_buff_size,
            ),
        )

        message_builder__adv = self.message_builder.for_sub_component('adv')
        adv = self._resolve_adv(ddv, message_builder__adv)
        self._check_adv(adv, full_resolving_env, message_builder__adv)

        primitive = self._resolve_primitive_value(adv, full_resolving_env.application_environment)

        return self._check_primitive(primitive, full_resolving_env,
                                     self.message_builder.for_sub_component('primitive'))

    def _resolve_ddv(self,
                     sdv: FullDepsSdv[PRIMITIVE],
                     message_builder: asrt.MessageBuilder,
                     ) -> FullDepsDdv[PRIMITIVE]:
        ddv = sdv.resolve(self.arrangement.symbols)

        asrt.is_instance(FullDepsDdv).apply(self.put,
                                            ddv,
                                            message_builder)

        assert isinstance(ddv, FullDepsDdv)

        return ddv

    def _resolve_adv(self, ddv: FullDepsDdv[PRIMITIVE],
                     message_builder: MessageBuilder) -> ApplicationEnvironmentDependentValue[PRIMITIVE]:
        adv = ddv.value_of_any_dependency(self.tcds)

        asrt.is_instance(ApplicationEnvironmentDependentValue).apply(
            self.put,
            adv,
            message_builder,
        )
        return adv

    def _resolve_primitive_value(self,
                                 adv: ApplicationEnvironmentDependentValue[PRIMITIVE],
                                 application_environment: ApplicationEnvironment) -> PRIMITIVE:
        return adv.primitive(application_environment)

    def _check_validation_pre_sds(self,
                                  matcher_ddv: FullDepsDdv[PRIMITIVE],
                                  message_builder: MessageBuilder):
        validator = matcher_ddv.validator
        result = validator.validate_pre_sds_if_applicable(self.hds)

        self.execution.validation.pre_sds.apply_with_message(self.put,
                                                             result,
                                                             message_builder.apply('validation pre sds'))

        if result is not None:
            raise StopAssertion()

    def _check_validation_post_sds(self, matcher_ddv: FullDepsDdv[PRIMITIVE],
                                   message_builder: MessageBuilder):
        validator = matcher_ddv.validator
        result = validator.validate_post_sds_if_applicable(self.tcds)

        self.execution.validation.post_sds.apply_with_message(self.put,
                                                              result,
                                                              message_builder.apply('validation post sds'))

        if result is not None:
            raise StopAssertion()

    def _check_adv(self,
                   adv: ApplicationEnvironmentDependentValue[PRIMITIVE],
                   resolving_env: FullResolvingEnvironment,
                   message_builder: MessageBuilder,
                   ):
        env = AssertionResolvingEnvironment(resolving_env.tcds,
                                            resolving_env.application_environment)
        assertion = self.adv(env)
        assertion.apply(self.put, adv, message_builder)

    def _check_primitive(self,
                         primitive: PRIMITIVE,
                         resolving_env: FullResolvingEnvironment,
                         message_builder: MessageBuilder,
                         ) -> _ValueAssertionApplier:
        self.common_properties.check_primitive(self.put,
                                               primitive,
                                               message_builder,
                                               )
        assertion_on_primitive = self.primitive(AssertionResolvingEnvironment(resolving_env.tcds,
                                                                              resolving_env.application_environment))
        assertion_on_primitive.apply(self.put, primitive, message_builder)

        try:
            result = self.applier.apply(self.put, message_builder, primitive, resolving_env, self.model_constructor)

            if self.execution.is_hard_error is not None:
                self.put.fail(message_builder.apply('HARD_ERROR not reported (raised)'))

            self.common_properties.check_application_output(
                self.put,
                result,
                message_builder.for_sub_component('common properties of output')
            )
            return _ValueAssertionApplier(
                self.execution.main_result,
                result,
                message_builder.for_sub_component('output'),
            )
        except HardErrorException as ex:
            return self._check_hard_error(ex, message_builder)

    def _check_hard_error(self,
                          result: HardErrorException,
                          message_builder: asrt.MessageBuilder,
                          ) -> _ValueAssertionApplier:
        if self.execution.is_hard_error is None:
            err_msg_str = print_.print_to_str(result.error.render_sequence())
            self.put.fail(message_builder.apply('Unexpected HARD_ERROR:\n') +
                          err_msg_str)
        else:
            return _ValueAssertionApplier(
                self.execution.is_hard_error,
                result.error,
                message_builder.for_sub_component('hard error'),
            )
