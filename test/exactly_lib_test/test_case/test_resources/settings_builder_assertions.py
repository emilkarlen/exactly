import unittest
from typing import Optional, Callable, Dict

from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.act.adv_w_validation import AdvWValidation
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.setup.settings_builder import SetupSettingsBuilder
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib_test.test_case.test_resources import adv_w_validation_assertions as asrt_adv_w_validation
from exactly_lib_test.test_case.test_resources.adv_w_validation_assertions import AdvWvAssertionModel, T
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion, AssertionBase, \
    MessageBuilder


class SettingsBuilderAssertionModel(tuple):
    def __new__(cls,
                actual: SetupSettingsBuilder,
                environment: InstructionEnvironmentForPostSdsStep,
                os_services: OsServices,
                ):
        return tuple.__new__(cls, (actual, environment, os_services))

    @property
    def actual(self) -> SetupSettingsBuilder:
        return self[0]

    @property
    def environment(self) -> InstructionEnvironmentForPostSdsStep:
        return self[1]

    @property
    def os_services(self) -> OsServices:
        return self[2]


def matches(stdin: Assertion[Optional[AdvWvAssertionModel[StringSource]]] = asrt.anything_goes(),
            environ: Assertion[Optional[Dict[str, str]]] = asrt.is_none_or_instance(dict)
            ) -> Assertion[SettingsBuilderAssertionModel]:
    return asrt.is_instance_with__many(
        SettingsBuilderAssertionModel,
        [
            asrt.sub_component(
                'environ',
                _get_environ,
                environ,
            ),
            _OptionalSettingsBuilderComponentAssertion(
                'stdin',
                _get_stdin,
                stdin,
            ),
        ]
    )


def stdin_is_not_present() -> Assertion[SettingsBuilderAssertionModel]:
    return matches(stdin=asrt.is_none)


def stdin_is_present_but_invalid() -> Assertion[SettingsBuilderAssertionModel]:
    return matches(
        stdin=asrt.is_not_none_and(asrt_adv_w_validation.is_invalid())
    )


def stdin_is_present_and_valid(expected: Assertion[StringSource]
                               ) -> Assertion[SettingsBuilderAssertionModel]:
    return matches(
        stdin=asrt.is_not_none_and(asrt_adv_w_validation.is_valid(expected))
    )


class _OptionalSettingsBuilderComponentAssertion(AssertionBase[SettingsBuilderAssertionModel]):
    def __init__(self,
                 name: str,
                 component_getter: Callable[[SetupSettingsBuilder], Optional[AdvWValidation[T]]],
                 component: Assertion[Optional[AdvWvAssertionModel[T]]],
                 ):
        self._name = name
        self._component_getter = component_getter
        self._component = component

    def _apply(self,
               put: unittest.TestCase,
               value: SettingsBuilderAssertionModel,
               message_builder: MessageBuilder,
               ):
        component = self._component_getter(value.actual)

        app_env = ApplicationEnvironment(
            value.os_services,
            value.environment.proc_exe_settings,
            value.environment.tmp_dir__path_access.paths_access,
            value.environment.mem_buff_size,
        )
        component_model = (
            None
            if component is None
            else
            AdvWvAssertionModel(app_env, component)
        )

        self._component.apply(
            put,
            component_model,
            message_builder.for_sub_component(self._name)
        )


def _get_stdin(x: SetupSettingsBuilder) -> Optional[AdvWValidation[StringSource]]:
    return x.stdin


def _get_environ(x: SettingsBuilderAssertionModel) -> Optional[Dict[str, str]]:
    return x.actual.environ
