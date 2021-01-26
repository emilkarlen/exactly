import unittest
from typing import Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.execution.partial_execution import setup_settings_handler as sut
from exactly_lib.impls.types.string_source.factory import RootStringSourceFactory
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.test_case.phases.act.execution_input import ActExecutionInput
from exactly_lib.test_case.phases.setup.settings_handler import SetupSettingsHandler
from exactly_lib.type_val_deps.dep_variants.adv_w_validation.impls import ConstantAdvWValidation, \
    unconditionally_successful_validator
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.file_utils.dir_file_spaces import DirFileSpaceThatMustNoBeUsed
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.tcfs.test_resources.fake_ds import fake_tcds
from exactly_lib_test.test_case.test_resources import adv_w_validation_assertions as asrt_adv_w
from exactly_lib_test.test_case.test_resources import instruction_environment
from exactly_lib_test.test_case.test_resources import settings_builder_assertions as asrt_settings_builder
from exactly_lib_test.test_case.test_resources.adv_w_validation_assertions import AdvWvAssertionModel
from exactly_lib_test.test_case.test_resources.os_services_that_raises import OsServicesThatRaises
from exactly_lib_test.test_case.test_resources.settings_builder_assertions import SettingsBuilderAssertionModel
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase, \
    MessageBuilder


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestConstructionOfEmpty(),
        TestSetStdinToNone(),
        TestSetStdinToValidValue(),
        TestSetStdinToInvalidValue(),
    ])


class Expectation:
    def __init__(self,
                 settings_builder: ValueAssertion[SettingsBuilderAssertionModel],
                 act_execution_info: ValueAssertion[AdvWvAssertionModel],
                 ):
        self.settings_builder = settings_builder
        self.act_execution_info = act_execution_info


class TestConstructionOfEmpty(unittest.TestCase):
    def runTest(self):
        # ACT #
        actual = sut.StandardSetupSettingsHandler.new_empty()
        # ASSERT #
        expectation = _Assertion(
            settings_builder=asrt_settings_builder.stdin_is_not_present(),
            act_execution_info=asrt_adv_w.is_valid(
                resolved_value=_resolved_stdin(asrt.is_none),
            )
        )

        expectation.apply_without_message(self, actual)


class TestSetStdinToNone(unittest.TestCase):
    def runTest(self):
        # ACT #
        actual = sut.StandardSetupSettingsHandler.new_empty()
        actual.builder.stdin = None
        # ASSERT #
        expectation = _Assertion(
            settings_builder=asrt_settings_builder.stdin_is_not_present(),
            act_execution_info=asrt_adv_w.is_valid(
                resolved_value=_resolved_stdin(asrt.is_none),
            )
        )

        expectation.apply_without_message(self, actual)


class TestSetStdinToValidValue(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        string_source_factory = RootStringSourceFactory(DirFileSpaceThatMustNoBeUsed())
        stdin_contents = 'the contents of stdin'
        string_source_to_set = string_source_factory.of_const_str(stdin_contents)
        # ACT #
        actual = sut.StandardSetupSettingsHandler.new_empty()
        actual.builder.stdin = ConstantAdvWValidation(
            string_source_to_set,
            validator=unconditionally_successful_validator,
        )
        # ASSERT #
        expected_string_source = _contents_as_str_equals(stdin_contents)
        expectation = _Assertion(
            settings_builder=asrt_settings_builder.stdin_is_present_and_valid(expected_string_source),
            act_execution_info=asrt_adv_w.is_valid(
                resolved_value=_resolved_stdin(expected_string_source),
            )
        )

        expectation.apply_without_message(self, actual)


class TestSetStdinToInvalidValue(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        string_source_factory = RootStringSourceFactory(DirFileSpaceThatMustNoBeUsed())
        string_source_to_set = string_source_factory.of_const_str('value of invalid string source')
        # ACT #
        actual = sut.StandardSetupSettingsHandler.new_empty()
        actual.builder.stdin = ConstantAdvWValidation(
            string_source_to_set,
            validator=unconditionally_unsuccessful_validator,
        )
        # ASSERT #
        expectation = _Assertion(
            settings_builder=asrt_settings_builder.stdin_is_present_but_invalid(),
            act_execution_info=asrt_adv_w.is_invalid()
        )

        expectation.apply_without_message(self, actual)


class _Assertion(ValueAssertionBase[SetupSettingsHandler]):
    FAKE_TCDS = fake_tcds()
    ENVIRONMENT = instruction_environment.fake_post_sds_environment()
    OS_SERVICES = OsServicesThatRaises()

    def __init__(self,
                 settings_builder: ValueAssertion[SettingsBuilderAssertionModel],
                 act_execution_info: ValueAssertion[AdvWvAssertionModel[ActExecutionInput]],
                 ):
        self._settings_builder = settings_builder
        self._act_execution_info = act_execution_info

    def _apply(self,
               put: unittest.TestCase,
               value: SetupSettingsHandler,
               message_builder: MessageBuilder,
               ):
        settings_builder_model = asrt_settings_builder.SettingsBuilderAssertionModel(
            value.builder,
            self.ENVIRONMENT,
            self.OS_SERVICES,
        )

        self._settings_builder.apply(
            put,
            settings_builder_model,
            message_builder.for_sub_component('settings builder'),
        )

        aei_model = AdvWvAssertionModel(
            ApplicationEnvironment(self.OS_SERVICES,
                                   self.ENVIRONMENT.proc_exe_settings,
                                   self.ENVIRONMENT.tmp_dir__path_access.paths_access,
                                   self.ENVIRONMENT.mem_buff_size,
                                   ),
            value.as_act_execution_input(),
        )

        self._act_execution_info.apply(
            put,
            aei_model,
            message_builder.for_sub_component('act execution info'),
        )


def _resolved_stdin(expectation: ValueAssertion[Optional[StringSource]]) -> ValueAssertion[ActExecutionInput]:
    return asrt.sub_component(
        'stdin',
        _get_stdin,
        expectation,
    )


def _get_stdin(x: ActExecutionInput) -> Optional[StringSource]:
    return x.stdin


def _get_contents_as_str(x: StringSource) -> str:
    return x.contents().as_str


def _contents_as_str_equals(expected: str) -> ValueAssertion[StringSource]:
    return asrt.sub_component(
        'contents as str',
        _get_contents_as_str,
        asrt.equals(expected)
    )


def unconditionally_unsuccessful_validator() -> Optional[TextRenderer]:
    return asrt_text_doc.new_single_string_text_for_test('the err msg')


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
