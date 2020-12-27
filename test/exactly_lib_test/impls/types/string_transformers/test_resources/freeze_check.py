import unittest
from typing import Callable, Sequence

from exactly_lib.type_val_deps.dep_variants.adv.app_env_dep_val import ApplicationEnvironmentDependentValue
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.type_val_prims.string_transformer import StringTransformer
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import AssertionResolvingEnvironment
from exactly_lib_test.test_resources.recording import SequenceRecorder
from exactly_lib_test.test_resources.value_assertions import sequence_assertions as asrt_seq
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase, \
    MessageBuilder
from exactly_lib_test.type_val_prims.string_source.test_resources import string_sources, properties_access
from exactly_lib_test.type_val_prims.string_source.test_resources.string_sources import StringSourceMethod


def check(put: unittest.TestCase,
          mk_transformer: Callable[[StringSource], StringSource],
          source_may_depend_on_external_resources: bool,
          num_initial_freeze_invocations: int,
          tmp_file_space: DirFileSpace,
          source_model_method_invocations: ValueAssertion[Sequence[StringSourceMethod]],
          message_builder: asrt.MessageBuilder = asrt.new_message_builder(),
          source_model_contents: str = '1\n2\n3\n',
          ):
    source_model_invocations_recorder = _new_recorder()

    source_model = string_sources.of_string(source_model_contents,
                                            tmp_file_space,
                                            source_may_depend_on_external_resources)
    source_model_w_invocations_recording = string_sources.StringSourceThatRecordsMethodInvocations(
        source_model,
        source_model_invocations_recorder,
    )
    checked_string_source = mk_transformer(source_model_w_invocations_recording)
    # ACT #
    _invoke_freeze(checked_string_source, num_initial_freeze_invocations)
    _invoke_every_contents_method(checked_string_source)
    # ASSERT #
    source_model_method_invocations.apply(put,
                                          source_model_invocations_recorder.recordings,
                                          message_builder.for_sub_component('invoked methods of the source model'))


def at_least_one_method_invocation_with_freeze_first() -> ValueAssertion[Sequence[StringSourceMethod]]:
    return asrt_seq.is_non_empty_and_first_element(
        asrt.equals(StringSourceMethod.FREEZE)
    )


def single_method_invocation_that_is(method: StringSourceMethod) -> ValueAssertion[Sequence[StringSourceMethod]]:
    return asrt.equals([method])


def exactly_one_method_invocation__and_that_is_not_freeze() -> ValueAssertion[Sequence[StringSourceMethod]]:
    return asrt.matches_sequence([asrt.is_not(StringSourceMethod.FREEZE)])


def first_invoked_method_of_source_model__is_freeze(
        environment: AssertionResolvingEnvironment
) -> ValueAssertion[ApplicationEnvironmentDependentValue[StringTransformer]]:
    """Checks freezing.
    Note: An assertion on the ADV (as this is) is not needed for this test -
    a test on the PRIMITIVE = StringTransformer - would do too.

    An ADV-assertion is used just because it was not used for other purposes -
    making it easy to utilize for this purpose.
    """
    return SourceModelMethodInvocationsAssertion(
        environment,
        at_least_one_method_invocation_with_freeze_first(),
    )


def single_access_of_source_model_after_freeze__that_is_not_freeze(
        environment: AssertionResolvingEnvironment
) -> ValueAssertion[ApplicationEnvironmentDependentValue[StringTransformer]]:
    """Checks freezing.
    Note: An assertion on the ADV (as this is) is not needed for this test -
    a test on the PRIMITIVE = StringTransformer - would do too.

    An ADV-assertion is used just because it was not used for other purposes -
    making it easy to utilize for this purpose.
    """
    return SourceModelMethodInvocationsAssertion(
        environment,
        exactly_one_method_invocation__and_that_is_not_freeze(),
    )


def _invoke_freeze(string_source: StringSource, num_times: int):
    for _ in range(num_times):
        string_source.freeze()


def _invoke_every_contents_method(string_source: StringSource):
    contents = string_source.contents()
    for method_case in properties_access.ALL_CASES__WO_LINES_ITER_CHECK:
        method_case.value(contents)


def _new_recorder() -> SequenceRecorder[StringSourceMethod]:
    return SequenceRecorder()


class SourceModelMethodInvocationsAssertion(
    ValueAssertionBase[ApplicationEnvironmentDependentValue[StringTransformer]]
):
    def __init__(self, environment: AssertionResolvingEnvironment,
                 source_model_method_invocations: ValueAssertion[Sequence[StringSourceMethod]],
                 ):
        self._environment = environment
        self._source_model_method_invocations = source_model_method_invocations

    def _apply(self,
               put: unittest.TestCase,
               value: ApplicationEnvironmentDependentValue[StringTransformer],
               message_builder: MessageBuilder,
               ):
        string_transformer = value.primitive(self._environment.app_env)
        for source_model_may_depend_on_external_resources in [False, True]:
            for num_invocations_of_freeze_before_check in [1, 2]:
                case_msg_builder = (
                    message_builder
                        .for_sub_component('source_model_may_depend_on_external_resources=' +
                                           str(source_model_may_depend_on_external_resources))
                        .for_sub_component(str(num_invocations_of_freeze_before_check) +
                                           ' invocations of freeze before check')
                )
                check(put,
                      string_transformer.transform,
                      source_model_may_depend_on_external_resources,
                      num_invocations_of_freeze_before_check,
                      self._environment.app_env.tmp_files_space,
                      source_model_method_invocations=self._source_model_method_invocations,
                      message_builder=case_msg_builder,
                      )
